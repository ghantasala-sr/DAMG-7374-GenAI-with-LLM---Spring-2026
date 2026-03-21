import json
import os

import serpapi
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send

from config import llm, llm_low_temp
from schemas import AgentState, ResearcherState

serp_client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))


def search_web(query: str, num_results: int = 5) -> str:
    try:
        results = serp_client.search(q=query, engine="google", hl="en", gl="us")
        organic = results.get("organic_results", [])[:num_results]
        if not organic:
            return ""
        snippets = []
        for i, item in enumerate(organic, 1):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            snippets.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")
        return "\n\n".join(snippets)
    except Exception as e:
        print(f"  [SerpAPI Error]: {e}")
        return ""


def supervisor_node(state: AgentState) -> dict:
    print("\n" + "=" * 60)
    print("SUPERVISOR: Decomposing topic into sub-topics...")
    print("=" * 60)

    messages = [
        SystemMessage(content=(
            "You are a research supervisor. Given a topic, decompose it into exactly 3 "
            "distinct sub-topics that together provide comprehensive coverage. "
            "Return ONLY a valid JSON object with key 'sub_topics' containing a list of 3 strings. "
            "Example: {\"sub_topics\": [\"sub-topic 1\", \"sub-topic 2\", \"sub-topic 3\"]}"
        )),
        HumanMessage(content=f"Decompose this topic into 3 sub-topics: {state['topic']}")
    ]

    response = llm_low_temp.invoke(messages)
    content = response.content.strip()

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        parsed = json.loads(content)
        sub_topics = parsed.get("sub_topics", [])[:3]
    except (json.JSONDecodeError, KeyError):
        sub_topics = [
            f"{state['topic']} - Historical Context",
            f"{state['topic']} - Current State",
            f"{state['topic']} - Future Outlook",
        ]

    for i, st in enumerate(sub_topics, 1):
        print(f"  Sub-topic {i}: {st}")

    return {"sub_topics": sub_topics}


def assign_researchers(state: AgentState):
    return [
        Send("researcher", {"sub_topic": topic, "research_results": []})
        for topic in state["sub_topics"]
    ]


def researcher_node(state: ResearcherState) -> dict:
    sub_topic = state["sub_topic"]
    print(f"\n  RESEARCHER: Researching '{sub_topic}'...")

    print(f"  RESEARCHER: Searching the web for '{sub_topic}'...")
    web_results = search_web(sub_topic)
    if web_results:
        print(f"  RESEARCHER: Found web results ({len(web_results)} chars)")
    else:
        print(f"  RESEARCHER: No web results found, using LLM knowledge only")

    web_context = ""
    if web_results:
        web_context = (
            f"\n\nBelow are real-time web search results for reference. "
            f"Use these to ground your research with current facts and sources:\n\n{web_results}"
        )

    messages = [
        SystemMessage(content=(
            "You are an expert researcher. Conduct thorough research on the given sub-topic. "
            "Provide key findings, statistics, expert opinions, and relevant examples. "
            "Be factual, detailed, and cite specific information where possible. "
            "If web search results are provided, incorporate those findings and cite the sources. "
            "Keep your research summary to 2-3 paragraphs."
        )),
        HumanMessage(content=f"Research the following sub-topic thoroughly: {sub_topic}{web_context}")
    ]

    response = llm.invoke(messages)
    finding = f"## Research: {sub_topic}\n\n{response.content.strip()}"
    print(f"  RESEARCHER: Completed research on '{sub_topic}' ({len(response.content)} chars)")

    return {"research_results": [finding]}


def generator_node(state: AgentState) -> dict:
    revision_count = state.get("revision_count", 0)
    critique = state.get("critique", "")
    draft = state.get("draft", "")

    if revision_count == 0:
        print("\n" + "=" * 60)
        print("GENERATOR: Writing initial draft from research...")
        print("=" * 60)
    else:
        print(f"\n" + "=" * 60)
        print(f"GENERATOR: Revising draft (iteration {revision_count + 1})...")
        print("=" * 60)

    research_context = "\n\n".join(state.get("research_results", []))

    if revision_count == 0:
        system_content = (
            "You are an expert article writer. Using the research provided, write a comprehensive, "
            "well-structured article. Include:\n"
            "- An engaging introduction\n"
            "- Clear sections with headings\n"
            "- Key findings and analysis\n"
            "- A compelling conclusion\n"
            "Write in a professional yet accessible tone. Target 500-700 words."
        )
        user_content = (
            f"Write a comprehensive article on: {state['topic']}\n\n"
            f"Use the following research as your source material:\n\n{research_context}"
        )
    else:
        system_content = (
            "You are an expert article writer revising your work based on editorial feedback. "
            "Address ALL points raised in the critique. Maintain the article's strengths while "
            "fixing weaknesses. Incorporate the specific suggestions provided. "
            "Do not reduce quality in areas already strong."
        )
        user_content = (
            f"Topic: {state['topic']}\n\n"
            f"Your previous draft:\n{draft}\n\n"
            f"Editorial critique and feedback:\n{critique}\n\n"
            f"Please revise the article addressing all the feedback above."
        )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    new_draft = response.content.strip()

    print(f"  Draft length: {len(new_draft)} characters")

    return {
        "draft": new_draft,
        "revision_count": revision_count + 1,
    }


def reflector_node(state: AgentState) -> dict:
    print("\n" + "=" * 60)
    print(f"REFLECTOR: Critiquing draft (revision #{state.get('revision_count', 1)})...")
    print("=" * 60)

    draft = state["draft"]
    topic = state.get("topic", "")

    print(f"  REFLECTOR: Fact-checking claims via web search...")
    fact_check_results = search_web(f"{topic} facts statistics latest research")
    fact_context = ""
    if fact_check_results:
        print(f"  REFLECTOR: Retrieved fact-check context ({len(fact_check_results)} chars)")
        fact_context = (
            f"\n\nUse the following real-time web search results to verify factual claims "
            f"in the article. Flag any inaccuracies or outdated information:\n\n{fact_check_results}"
        )
    else:
        print(f"  REFLECTOR: No fact-check results, evaluating without web context")

    revision_count = state.get("revision_count", 0)

    messages = [
        SystemMessage(content=(
            "You are a senior editor and fact-checker. Critically evaluate the article draft below. "
            "You have access to real-time web search results to verify factual claims.\n\n"
            "Assess it on these criteria, scoring EACH from 1.0 to 10.0:\n"
            "1. Accuracy — Are facts, statistics, and claims correct per the web search results?\n"
            "2. Completeness — Does it cover all important aspects of the topic?\n"
            "3. Clarity — Is the writing clear, concise, and easy to understand?\n"
            "4. Structure — Is it well-organized with logical flow between sections?\n"
            "5. Engagement — Is it compelling and interesting to read?\n\n"
            "Compute the overall score as the AVERAGE of the 5 criteria scores.\n"
            f"This is revision #{revision_count}. "
            "If this is a revision, check whether previous weaknesses have been addressed.\n\n"
            "Return ONLY a valid JSON object with these keys:\n"
            "- \"accuracy_score\": float 1.0-10.0\n"
            "- \"completeness_score\": float 1.0-10.0\n"
            "- \"clarity_score\": float 1.0-10.0\n"
            "- \"structure_score\": float 1.0-10.0\n"
            "- \"engagement_score\": float 1.0-10.0\n"
            "- \"score\": float (average of the 5 above)\n"
            "- \"strengths\": list of strength strings\n"
            "- \"weaknesses\": list of weakness strings\n"
            "- \"factual_issues\": list of any factual errors found (empty list if none)\n"
            "- \"suggestions\": list of specific actionable improvement strings\n\n"
            "Be rigorous. A score of 8+ means publication-ready. "
            "Do NOT default to 7.5 — differentiate clearly between drafts."
        )),
        HumanMessage(content=f"Critique this article:\n\n{draft}{fact_context}")
    ]

    response = llm_low_temp.invoke(messages)
    content = response.content.strip()

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        parsed = json.loads(content)

        sub_scores = {
            "Accuracy": float(parsed.get("accuracy_score", 5.0)),
            "Completeness": float(parsed.get("completeness_score", 5.0)),
            "Clarity": float(parsed.get("clarity_score", 5.0)),
            "Structure": float(parsed.get("structure_score", 5.0)),
            "Engagement": float(parsed.get("engagement_score", 5.0)),
        }
        score = float(parsed.get("score", sum(sub_scores.values()) / len(sub_scores)))
        strengths = parsed.get("strengths", [])
        weaknesses = parsed.get("weaknesses", [])
        factual_issues = parsed.get("factual_issues", [])
        suggestions = parsed.get("suggestions", [])
    except (json.JSONDecodeError, KeyError, ValueError):
        score = 6.0
        sub_scores = {}
        strengths = ["Article was generated successfully"]
        weaknesses = ["Could not parse structured critique"]
        factual_issues = []
        suggestions = ["Improve overall quality and depth"]

    critique_text = f"Score: {score}/10\n\n"
    if sub_scores:
        critique_text += "Sub-scores:\n"
        critique_text += "\n".join(f"  {k}: {v}/10" for k, v in sub_scores.items())
        critique_text += "\n\n"
    critique_text += "Strengths:\n" + "\n".join(f"  + {s}" for s in strengths) + "\n\n"
    critique_text += "Weaknesses:\n" + "\n".join(f"  - {w}" for w in weaknesses) + "\n\n"
    if factual_issues:
        critique_text += "Factual Issues:\n" + "\n".join(f"  ! {f}" for f in factual_issues) + "\n\n"
    critique_text += "Suggestions:\n" + "\n".join(f"  * {s}" for s in suggestions)

    print(f"  Score: {score}/10")
    if sub_scores:
        for k, v in sub_scores.items():
            print(f"    {k}: {v}/10")
    print(f"  Strengths: {len(strengths)} | Weaknesses: {len(weaknesses)} | Factual Issues: {len(factual_issues)}")

    return {
        "critique": critique_text,
        "score": score,
    }


def evaluator_node(state: AgentState) -> dict:
    score = state.get("score", 0.0)
    revision_count = state.get("revision_count", 0)
    max_revisions = 3

    print("\n" + "=" * 60)
    print(f"EVALUATOR: Score={score}/10 | Revision={revision_count}/{max_revisions}")
    print("=" * 60)

    if score >= 8.0:
        decision = "accept"
        reasoning = f"Article meets quality threshold (score: {score}/10). Ready for publication."
    elif revision_count >= max_revisions:
        decision = "accept"
        reasoning = f"Maximum revision limit reached ({max_revisions}). Accepting current draft (score: {score}/10)."
    else:
        decision = "revise"
        reasoning = f"Score {score}/10 is below threshold (8.0). Sending back for revision {revision_count + 1}."

    print(f"  Decision: {decision.upper()}")
    print(f"  Reasoning: {reasoning}")

    return {
        "eval_decision": decision,
    }


def finalizer_node(state: AgentState) -> dict:
    print("\n" + "=" * 60)
    print("FINALIZER: Preparing final output...")
    print("=" * 60)

    final_output = (
        f"{'=' * 60}\n"
        f"FINAL ARTICLE\n"
        f"{'=' * 60}\n"
        f"Topic: {state['topic']}\n"
        f"Quality Score: {state.get('score', 'N/A')}/10\n"
        f"Revisions: {state.get('revision_count', 0)}\n"
        f"Sub-topics Researched: {', '.join(state.get('sub_topics', []))}\n"
        f"{'=' * 60}\n\n"
        f"{state.get('draft', 'No draft available')}\n\n"
        f"{'=' * 60}\n"
        f"END OF ARTICLE\n"
        f"{'=' * 60}"
    )

    return {"final_output": final_output}
