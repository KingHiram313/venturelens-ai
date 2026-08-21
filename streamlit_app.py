
import json, re
from datetime import datetime
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="VentureLens AI", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.7rem;}
.small-note {color:#6b7280;font-size:.85rem}
</style>
""", unsafe_allow_html=True)

SYSTEM = """You are VentureLens AI, an AI-native venture and GTM research analyst.
Turn an ambiguous product, technology, or venture into a testable commercial strategy.
Use current web research. Clearly distinguish facts from hypotheses. Never present market sizing as
certain unless sourced; show assumptions and prefer bottom-up sizing. Identify direct/indirect competitors,
substitutes, build-vs-buy and status quo. Identify real target accounts and lookalikes using observable
signals. If existing customers are supplied, infer patterns and identify similar prospects. Map economic
buyers, technical buyers, champions, procurement and blockers. Treat pain points as hypotheses unless
public evidence supports them. For every major risk propose a fast validation experiment. Outreach must
tie a reason-to-contact to a role-specific hypothesis. Finish with INVEST, TEST, PIVOT, or PASS.
Return ONLY valid JSON. No markdown fences."""

SCHEMA = {
 "executive_summary":{"venture_attractiveness_score":0,"recommendation":"TEST","one_sentence_thesis":"","biggest_assumption_that_could_kill_it":"","confidence":"medium"},
 "market":{"market_definition":"","growth_drivers":[],"tam":{"estimate":"","method":"","assumptions":[],"confidence":""},"sam":{"estimate":"","method":"","assumptions":[],"confidence":""},"som":{"estimate":"","method":"","assumptions":[],"confidence":""}},
 "segments":[{"segment":"","why_it_fits":"","buying_trigger":"","priority":"PURSUE"}],
 "competitors":[{"company_or_alternative":"","type":"direct","why_relevant":"","threat_level":"medium"}],
 "target_accounts":[{"company":"","why_fit":"","observable_signal":"","priority":"PURSUE","confidence":"medium"}],
 "lookalike_prospects":[{"company":"","similar_to":"","shared_attributes":[],"why_now":"","priority":"TEST"}],
 "key_roles":[{"role":"","buying_role":"economic buyer","pain_hypotheses":[],"discovery_objective":"","likely_blockers":[]}],
 "partnerships":[{"partner_type":"","example_companies":[],"value_exchange":"","commercial_motion":""}],
 "outreach":[{"target_role":"","reason_to_contact":"","value_hypothesis":"","discovery_cta":"","sample_message":""}],
 "risks":[{"risk":"","probability":"medium","impact":"high","evidence_or_reasoning":"","fastest_validation":""}],
 "experiments":[{"experiment":"","what_it_tests":"","success_signal":"","time_horizon":""}],
 "sources":[{"title":"","url":"","supports":""}]
}

def parse_json(s):
    s=s.strip()
    try: return json.loads(s)
    except Exception:
        m=re.search(r"\{.*\}",s,re.S)
        if not m: raise ValueError("Model output was not valid JSON.")
        return json.loads(m.group(0))

def get_key():
    # Deployment: secret owned by app creator. Local fallback: user can enter a key.
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"], True
    except Exception:
        pass
    return st.session_state.get("local_api_key",""), False

def analyze(key, model, vals):
    client=OpenAI(api_key=key)
    prompt=f"""Analyze this opportunity:
PRODUCT / VENTURE: {vals['product']}
DESCRIPTION: {vals['description']}
GEOGRAPHY: {vals['geography']}
INITIAL TARGET MARKET: {vals['target_market']}
EXISTING CUSTOMERS / PROOF POINTS: {vals['existing_customers'] or 'None supplied'}
KNOWN COMPETITORS / ALTERNATIVES: {vals['known_competitors'] or 'None supplied'}
COMMERCIAL OBJECTIVE: {vals['objective']}

Generate: projected TAM/SAM/SOM with assumptions; segmentation and ICP; real target accounts; lookalikes;
customer lookalikes if customers are supplied; key roles; pain hypotheses; buying triggers; competitors;
partnership opportunities; targeted outreach; risks; validation experiments; and a final recommendation.
Include source URLs in the sources array.

Return ONLY JSON matching:
{json.dumps(SCHEMA)}"""
    resp=client.responses.create(
        model=model,
        tools=[{"type":"web_search"}],
        input=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}]
    )
    return parse_json(resp.output_text)

st.title("🧭 VentureLens AI")
st.subheader("AI-native Venture & GTM Intelligence")
st.caption("From ambiguous opportunity → market thesis → target accounts → buyer roles → outreach → validation.")

api_key, deployed_secret = get_key()
with st.sidebar:
    st.header("Prototype")
    if deployed_secret:
        st.success("AI connection configured")
    else:
        st.text_input("OpenAI API key (local use)", type="password", key="local_api_key")
        st.caption("For a public deployment, configure OPENAI_API_KEY as a Streamlit secret instead.")
    model=st.text_input("OpenAI model", value="gpt-5.4")
    st.divider()
    st.markdown("**Decision workflow**")
    st.write("Market sizing")
    st.write("ICP & segmentation")
    st.write("Target accounts & lookalikes")
    st.write("Buyer roles & pain hypotheses")
    st.write("Competition & partnerships")
    st.write("Outreach")
    st.write("Risks & experiments")

with st.form("venture_form"):
    c1,c2=st.columns(2)
    with c1:
        product=st.text_input("Product / venture", value="AI Infrastructure Optimization Platform")
        description=st.text_area("What it does", value="Helps AI infrastructure teams improve GPU utilization, forecast capacity, and reduce idle compute across mixed cloud and on-prem environments.", height=120)
        geography=st.selectbox("Primary geography", ["North America","United States","Global","Europe","Canada"])
    with c2:
        target_market=st.text_input("Initial target market", value="AI infrastructure teams at growth-stage technology companies")
        existing_customers=st.text_area("Existing customers / proof points", placeholder="Optional: customer names or archetypes", height=85)
        known_competitors=st.text_area("Known competitors / alternatives", placeholder="Optional", height=85)
        objective=st.selectbox("Commercial objective", ["Validate product-market fit","Build enterprise pipeline","Enter a new market","Find strategic partners"])
    submitted=st.form_submit_button("Run live AI analysis", type="primary", use_container_width=True)

if submitted:
    api_key,_=get_key()
    if not api_key:
        st.error("No API key is configured. For local use, enter one in the sidebar. For deployment, add OPENAI_API_KEY to Streamlit Secrets.")
    else:
        vals=locals()
        with st.spinner("Researching live market signals, companies, competitors and GTM options..."):
            try:
                st.session_state["result"]=analyze(api_key,model,vals)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

if "result" in st.session_state:
    r=st.session_state["result"]; es=r.get("executive_summary",{}); mk=r.get("market",{})
    st.divider(); st.header("Executive Decision")
    a,b,c,d=st.columns(4)
    a.metric("Attractiveness", f"{es.get('venture_attractiveness_score','—')}/100")
    b.metric("Recommendation", es.get("recommendation","—"))
    c.metric("Projected TAM", mk.get("tam",{}).get("estimate","—"))
    d.metric("Confidence", str(es.get("confidence","—")).title())
    st.info(es.get("one_sentence_thesis",""))
    st.warning("Biggest assumption that could kill it: "+es.get("biggest_assumption_that_could_kill_it",""))

    tabs=st.tabs(["Market","ICP","Targets","Roles & Pains","Competition","Partners","Outreach","Risks","Experiments","Sources","JSON"])
    with tabs[0]:
        st.write(mk.get("market_definition",""))
        st.markdown("**Growth drivers**")
        for x in mk.get("growth_drivers",[]): st.write("•",x)
        for k in ("tam","sam","som"):
            x=mk.get(k,{})
            st.markdown(f"### {k.upper()}: {x.get('estimate','—')}")
            st.write(x.get("method",""))
            for a0 in x.get("assumptions",[]): st.write("•",a0)
            st.caption("Confidence: "+str(x.get("confidence","—")))
    with tabs[1]: st.dataframe(r.get("segments",[]),use_container_width=True,hide_index=True)
    with tabs[2]:
        st.markdown("### Target accounts"); st.dataframe(r.get("target_accounts",[]),use_container_width=True,hide_index=True)
        st.markdown("### Lookalike prospects"); st.dataframe(r.get("lookalike_prospects",[]),use_container_width=True,hide_index=True)
    with tabs[3]: st.dataframe(r.get("key_roles",[]),use_container_width=True,hide_index=True)
    with tabs[4]: st.dataframe(r.get("competitors",[]),use_container_width=True,hide_index=True)
    with tabs[5]: st.dataframe(r.get("partnerships",[]),use_container_width=True,hide_index=True)
    with tabs[6]:
        for x in r.get("outreach",[]):
            st.markdown("### "+x.get("target_role","Target role"))
            st.write("**Reason to contact:**",x.get("reason_to_contact",""))
            st.write("**Value hypothesis:**",x.get("value_hypothesis",""))
            st.write("**Discovery CTA:**",x.get("discovery_cta",""))
            st.code(x.get("sample_message",""),language=None)
    with tabs[7]: st.dataframe(r.get("risks",[]),use_container_width=True,hide_index=True)
    with tabs[8]: st.dataframe(r.get("experiments",[]),use_container_width=True,hide_index=True)
    with tabs[9]:
        for s in r.get("sources",[]):
            u=s.get("url",""); t=s.get("title","Source"); sup=s.get("supports","")
            if u: st.markdown(f"- [{t}]({u}) — {sup}")
            else: st.write("•",t,"—",sup)
    with tabs[10]: st.json(r)

    st.download_button("Download analysis JSON",json.dumps(r,indent=2),
                       file_name=f"venturelens_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                       mime="application/json")
