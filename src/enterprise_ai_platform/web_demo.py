from __future__ import annotations

from fastapi.responses import HTMLResponse


DEMO_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>엔터프라이즈 AI 에이전트 플랫폼 데모</title>
  <style>
    :root {
      --bg: #f1ede3;
      --panel: rgba(255, 251, 245, 0.88);
      --panel-strong: #fffaf2;
      --ink: #17130d;
      --muted: #665b4a;
      --accent: #b53f1d;
      --accent-2: #1f6a5e;
      --line: rgba(23, 19, 13, 0.1);
      --shadow: 0 24px 60px rgba(33, 22, 10, 0.12);
      --radius: 24px;
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; }
    body {
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(181, 63, 29, 0.18), transparent 34%),
        radial-gradient(circle at top right, rgba(31, 106, 94, 0.16), transparent 28%),
        linear-gradient(180deg, #f7f1e7 0%, var(--bg) 58%, #e7e0d2 100%);
    }

    .shell {
      width: min(1240px, calc(100vw - 28px));
      margin: 18px auto;
      padding: 18px;
      border-radius: 30px;
      background: rgba(255, 255, 255, 0.46);
      backdrop-filter: blur(18px);
      box-shadow: var(--shadow);
      border: 1px solid rgba(255, 255, 255, 0.55);
    }

    .hero,
    .grid-2 {
      display: grid;
      gap: 16px;
    }

    .hero {
      grid-template-columns: 1.2fr 0.8fr;
      margin-bottom: 16px;
    }

    .grid-2 {
      grid-template-columns: 1fr 1fr;
      margin-top: 16px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 22px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
    }

    .eyebrow {
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-size: 12px;
      color: var(--accent);
      margin-bottom: 10px;
    }

    h1 {
      margin: 0 0 10px;
      font-size: clamp(34px, 5vw, 60px);
      line-height: 0.95;
    }

    h2 {
      margin: 0 0 12px;
      font-size: 19px;
    }

    p, .subtle {
      color: var(--muted);
      line-height: 1.5;
      margin: 0;
    }

    .provider-chip,
    .status {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.74);
      font-size: 14px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--accent-2);
      box-shadow: 0 0 0 6px rgba(31, 106, 94, 0.12);
    }

    .explain-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 16px;
    }

    .concept {
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.62);
    }

    .concept strong {
      display: block;
      margin-bottom: 6px;
    }

    .stack {
      display: grid;
      gap: 12px;
    }

    .pick {
      padding: 14px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.62);
      cursor: pointer;
      transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    }

    .pick:hover,
    .pick.active {
      transform: translateY(-1px);
      border-color: rgba(181, 63, 29, 0.36);
      background: rgba(255, 250, 242, 0.96);
    }

    .row-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: start;
      margin-bottom: 8px;
    }

    .tag {
      display: inline-flex;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(31, 106, 94, 0.09);
      color: var(--accent-2);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .mono {
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 12px;
      color: var(--muted);
    }

    .controls {
      display: grid;
      gap: 12px;
      margin-top: 14px;
    }

    label {
      display: grid;
      gap: 8px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    input, textarea, button {
      font: inherit;
    }

    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--panel-strong);
      padding: 14px 16px;
      color: var(--ink);
    }

    textarea {
      min-height: 240px;
      resize: vertical;
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 13px;
      line-height: 1.5;
    }

    .button-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      cursor: pointer;
      transition: transform 160ms ease, opacity 160ms ease;
    }

    button:hover { transform: translateY(-1px); }
    button:disabled { opacity: 0.45; cursor: wait; }

    .primary {
      background: linear-gradient(135deg, var(--accent), #d07a32);
      color: white;
    }

    .secondary {
      background: rgba(31, 106, 94, 0.1);
      color: var(--accent-2);
      border: 1px solid rgba(31, 106, 94, 0.22);
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "SFMono-Regular", Consolas, monospace;
      font-size: 13px;
      line-height: 1.55;
      color: #201914;
    }

    .empty {
      padding: 18px;
      border-radius: 18px;
      border: 1px dashed rgba(23, 19, 13, 0.18);
      color: var(--muted);
      background: rgba(255, 255, 255, 0.42);
    }

    details {
      margin-top: 16px;
    }

    summary {
      cursor: pointer;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 12px;
    }

    .advanced-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 10px;
    }

    @media (max-width: 1080px) {
      .hero,
      .grid-2,
      .advanced-grid,
      .explain-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="card">
        <div class="eyebrow">엔터프라이즈 AI 에이전트 플랫폼</div>
        <h1>한 화면에서 보는 에이전트 데모</h1>
        <p>이 화면은 데모 발표용입니다. 복잡한 내부 개념을 줄이고, 지금 연결된 LLM과 단일 작업 실행, 멀티 단계 워크플로우만 먼저 보여줍니다.</p>
        <div class="explain-grid">
          <div class="concept">
            <strong>에이전트</strong>
            <div class="subtle">실제 일을 수행하는 구현체입니다. 예: 요약 에이전트, 번역 에이전트</div>
          </div>
          <div class="concept">
            <strong>Capability</strong>
            <div class="subtle">호출 가능한 기능 이름입니다. 예: `summarization`, `translation`</div>
          </div>
          <div class="concept">
            <strong>워크플로우</strong>
            <div class="subtle">여러 capability를 순서대로 연결한 작업 계획입니다.</div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="eyebrow">LLM 상태</div>
        <div id="providerBadge" class="provider-chip"><span class="dot"></span><span>제공자 정보를 불러오는 중</span></div>
        <div id="providerMeta" class="subtle" style="margin-top:12px;">제공자 설정을 확인하는 중입니다.</div>
        <div class="subtle" style="margin-top:12px;">이 데모는 OpenAI, Claude, Gemini, 또는 OpenAI 호환 오픈소스 모델 서버에 연결될 수 있습니다.</div>
      </div>
    </section>

    <section class="grid-2">
      <div class="card">
        <div class="row-top">
          <h2>단일 작업 실행</h2>
          <div id="resultStatus" class="status"><span class="dot"></span><span>대기 중</span></div>
        </div>
        <div class="subtle">하나의 capability를 선택해 즉시 실행합니다.</div>
        <div id="scenarioList" class="stack" style="margin-top:14px;"></div>
        <div class="controls">
          <label>
            API 키
            <input id="apiKey" type="password" value="dev-key" placeholder="X-API-Key 입력">
          </label>
          <label>
            Capability
            <input id="capabilityInput" type="text" placeholder="summarization">
          </label>
          <label>
            Payload JSON
            <textarea id="payloadInput" spellcheck="false"></textarea>
          </label>
        </div>
        <div class="button-row">
          <button id="runButton" class="primary">에이전트 실행</button>
          <button id="refreshButton" class="secondary">새로고침</button>
        </div>
        <div id="resultMeta" class="subtle" style="margin-top:14px;">시나리오를 선택한 뒤 실행하면 결과가 표시됩니다.</div>
        <pre id="resultOutput" class="empty" style="margin-top:12px;">아직 실행된 결과가 없습니다.</pre>
      </div>

      <div class="card">
        <div class="row-top">
          <h2>멀티 단계 워크플로우</h2>
          <button id="runWorkflowButton" class="primary" type="button">워크플로우 실행</button>
        </div>
        <div class="subtle">여러 capability가 함께 동작하는 예시입니다.</div>
        <div id="workflowList" class="stack" style="margin-top:14px;"></div>
        <div id="workflowMeta" class="subtle" style="margin-top:14px;">워크플로우를 실행하면 계획과 결과가 함께 표시됩니다.</div>
        <pre id="workflowOutput" class="empty" style="margin-top:12px;">아직 실행된 워크플로우가 없습니다.</pre>
      </div>
    </section>

    <details>
      <summary>고급 보기: Registry / Graph / Trace</summary>
      <div class="advanced-grid">
        <div class="card">
          <div class="row-top">
            <h2>Capability Registry</h2>
            <div class="mono" id="registryMeta">등록 정보를 불러오는 중입니다.</div>
          </div>
          <pre id="registryOutput" class="empty">Registry 정보를 불러오는 중입니다.</pre>
        </div>
        <div class="card">
          <div class="row-top">
            <h2>Capability Graph</h2>
            <button id="previewGraphButton" class="secondary" type="button">그래프 미리보기</button>
          </div>
          <div class="mono" id="graphMeta">입력 요청을 계획으로 분해합니다.</div>
          <pre id="graphOutput" class="empty" style="margin-top:12px;">그래프 미리보기를 실행하면 단계가 표시됩니다.</pre>
        </div>
      </div>
      <div class="advanced-grid">
        <div class="card">
          <h2>에이전트 목록</h2>
          <div class="subtle">플랫폼에 등록된 개별 에이전트 목록입니다.</div>
          <div id="capabilityList" class="stack" style="margin-top:14px;"></div>
        </div>
        <div class="card">
          <h2>트레이스 로그</h2>
          <div class="subtle">단일 작업 실행 후 내부 실행 단계가 표시됩니다.</div>
          <pre id="traceOutput" class="empty" style="margin-top:12px;">실행 후 트레이스가 표시됩니다.</pre>
        </div>
      </div>
    </details>
  </div>

  <script>
    const scenarioList = document.getElementById("scenarioList");
    const workflowList = document.getElementById("workflowList");
    const capabilityList = document.getElementById("capabilityList");
    const capabilityInput = document.getElementById("capabilityInput");
    const payloadInput = document.getElementById("payloadInput");
    const apiKeyInput = document.getElementById("apiKey");
    const providerBadge = document.getElementById("providerBadge");
    const providerMeta = document.getElementById("providerMeta");
    const resultStatus = document.getElementById("resultStatus");
    const resultMeta = document.getElementById("resultMeta");
    const resultOutput = document.getElementById("resultOutput");
    const workflowMeta = document.getElementById("workflowMeta");
    const workflowOutput = document.getElementById("workflowOutput");
    const registryMeta = document.getElementById("registryMeta");
    const registryOutput = document.getElementById("registryOutput");
    const graphMeta = document.getElementById("graphMeta");
    const graphOutput = document.getElementById("graphOutput");
    const traceOutput = document.getElementById("traceOutput");
    const runButton = document.getElementById("runButton");
    const runWorkflowButton = document.getElementById("runWorkflowButton");
    const refreshButton = document.getElementById("refreshButton");
    const previewGraphButton = document.getElementById("previewGraphButton");

    let scenarios = [];
    let workflows = [];
    let capabilities = [];

    function setStatus(label, accent = "#1f6a5e") {
      resultStatus.innerHTML = `<span class="dot" style="background:${accent}; box-shadow:0 0 0 6px ${accent}22;"></span><span>${label}</span>`;
    }

    function setOutput(target, text) {
      target.classList.remove("empty");
      target.textContent = text;
    }

    function samplePayloadForCapability(capability) {
      const scenario = scenarios.find((item) => item.request.capability === capability);
      if (scenario) {
        return scenario.request.payload;
      }
      return { text: "여기에 원하는 입력을 넣어 실행하세요." };
    }

    async function fetchJSON(path, options = {}) {
      const headers = { ...(options.headers || {}) };
      if (!path.endsWith("/health")) {
        headers["X-API-Key"] = apiKeyInput.value || "dev-key";
      }
      const response = await fetch(path, { ...options, headers });
      const text = await response.text();
      let data = {};
      try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
      if (!response.ok) {
        throw new Error(JSON.stringify(data, null, 2));
      }
      return data;
    }

    function renderScenarioCards(items) {
      scenarioList.innerHTML = "";
      items.forEach((scenario, index) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "pick";
        card.dataset.scenario = scenario.id;
        card.innerHTML = `
          <div class="row-top">
            <strong>${scenario.title}</strong>
            <span class="tag">${scenario.capability}</span>
          </div>
          <div class="mono">${scenario.id}</div>
        `;
        card.addEventListener("click", () => selectScenario(scenario.id));
        if (index === 0) {
          card.classList.add("active");
        }
        scenarioList.appendChild(card);
      });
    }

    function renderWorkflowCards(items) {
      workflowList.innerHTML = "";
      items.forEach((workflow, index) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "pick";
        card.dataset.workflow = workflow.id;
        card.innerHTML = `
          <div class="row-top">
            <strong>${workflow.title}</strong>
            <span class="tag">workflow</span>
          </div>
          <div class="mono">${workflow.expected_capabilities.join(" -> ")}</div>
        `;
        card.addEventListener("click", () => selectWorkflow(workflow.id));
        if (index === 0) {
          card.classList.add("active");
        }
        workflowList.appendChild(card);
      });
    }

    function renderCapabilities(items) {
      capabilityList.innerHTML = "";
      items.forEach((item) => {
        const card = document.createElement("div");
        card.className = "pick";
        card.innerHTML = `
          <div class="row-top">
            <strong>${item.name}</strong>
            <span class="tag">${item.category}</span>
          </div>
          <div class="subtle">${item.description}</div>
          <div class="mono" style="margin-top:8px;">${item.agent_id}</div>
        `;
        capabilityList.appendChild(card);
      });
    }

    function selectScenario(id) {
      const scenario = scenarios.find((item) => item.id === id);
      if (!scenario) return;
      document.querySelectorAll("[data-scenario]").forEach((node) => node.classList.remove("active"));
      const active = document.querySelector(`[data-scenario="${id}"]`);
      if (active) active.classList.add("active");
      capabilityInput.value = scenario.request.capability;
      payloadInput.value = JSON.stringify(scenario.request.payload, null, 2);
      graphMeta.textContent = `입력 요청: ${scenario.title}`;
    }

    function selectWorkflow(id) {
      const workflow = workflows.find((item) => item.id === id);
      if (!workflow) return;
      document.querySelectorAll("[data-workflow]").forEach((node) => node.classList.remove("active"));
      const active = document.querySelector(`[data-workflow="${id}"]`);
      if (active) active.classList.add("active");
      workflowMeta.textContent = `선택된 워크플로우: ${workflow.title}`;
    }

    async function refreshCatalog() {
      const [providerData, capabilityData, scenarioData, workflowData] = await Promise.all([
        fetchJSON("/v1/demo/providers"),
        fetchJSON("/v1/capabilities"),
        fetchJSON("/v1/demo/scenarios"),
        fetchJSON("/v1/demo/workflows")
      ]);

      const llm = providerData.llm;
      providerBadge.innerHTML = `<span class="dot"></span><span>${llm.provider} / ${llm.model}</span>`;
      providerMeta.textContent = `Base URL: ${llm.base_url || "n/a"} | 실사용 백엔드: ${llm.live} | API 키 설정 여부: ${llm.api_key_configured}`;

      capabilities = capabilityData.capabilities || [];
      scenarios = scenarioData.scenarios || [];
      workflows = workflowData.workflows || [];

      renderCapabilities(capabilities);
      renderScenarioCards(scenarios);
      renderWorkflowCards(workflows);

      registryMeta.textContent = `총 ${capabilities.length}개의 capability가 등록되어 있습니다.`;
      setOutput(
        registryOutput,
        JSON.stringify(
          capabilities.map((item) => ({
            capability: item.name,
            agent_id: item.agent_id,
            category: item.category
          })),
          null,
          2
        )
      );

      if (scenarios.length) {
        selectScenario(scenarios[0].id);
      }
      if (workflows.length) {
        selectWorkflow(workflows[0].id);
      }
    }

    async function previewGraph() {
      const scenario = scenarios.find((item) => item.request.capability === capabilityInput.value);
      const requestText = scenario ? scenario.title : capabilityInput.value;
      graphMeta.textContent = "Capability graph를 생성하는 중입니다.";
      setOutput(graphOutput, "계획을 계산하는 중입니다...");
      try {
        const body = await fetchJSON("/v1/demo/graph", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ request: requestText })
        });
        graphMeta.textContent = `입력 요청: ${body.request}`;
        setOutput(graphOutput, JSON.stringify(body.steps || [], null, 2));
      } catch (error) {
        graphMeta.textContent = "Capability graph 생성에 실패했습니다.";
        setOutput(graphOutput, String(error));
      }
    }

    async function runAgent() {
      let payload;
      try {
        payload = JSON.parse(payloadInput.value);
      } catch (error) {
        setStatus("JSON 오류", "#b53f1d");
        setOutput(resultOutput, String(error));
        return;
      }

      setStatus("실행 중", "#d07a32");
      resultMeta.textContent = "선택한 capability를 실행하고 있습니다.";
      setOutput(resultOutput, "선택한 에이전트를 실행 중입니다. 응답을 기다리는 중입니다...");
      setOutput(traceOutput, "실행이 끝나면 트레이스가 여기에 표시됩니다.");
      try {
        const body = await fetchJSON("/v1/agents/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            capability: capabilityInput.value,
            payload,
            config: {},
            context: {}
          })
        });
        const traceLines = (body.traces || []).map((entry) =>
          `${entry.step}. ${entry.action} | ${entry.input_summary} -> ${entry.output_summary} (${entry.duration_ms} ms)`
        );
        setStatus(body.status === "completed" ? "완료" : (body.status || "완료"), body.status === "completed" ? "#1f6a5e" : "#b53f1d");
        resultMeta.textContent = `에이전트: ${body.agent_id} | 실행 시간: ${body.duration_ms ?? "n/a"} ms`;
        setOutput(resultOutput, JSON.stringify(body.output || body.error || body, null, 2));
        setOutput(traceOutput, traceLines.length ? traceLines.join("\\n") : "반환된 트레이스가 없습니다.");
      } catch (error) {
        setStatus("실패", "#b53f1d");
        resultMeta.textContent = "실행이 실패했습니다.";
        setOutput(resultOutput, String(error));
        setOutput(traceOutput, "표시할 트레이스가 없습니다.");
      }
    }

    async function runWorkflow() {
      const active = document.querySelector("[data-workflow].active");
      const workflow = workflows.find((item) => item.id === (active ? active.dataset.workflow : workflows[0]?.id));
      if (!workflow) {
        workflowMeta.textContent = "실행할 워크플로우가 없습니다.";
        return;
      }

      workflowMeta.textContent = `워크플로우 실행 중: ${workflow.title}`;
      setOutput(workflowOutput, "여러 capability를 연결한 워크플로우를 실행하는 중입니다...");
      try {
        const body = await fetchJSON("/v1/demo/workflows/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ request: workflow.request, payload: workflow.payload })
        });
        workflowMeta.textContent = `상태: ${body.status} | 실행 시간: ${body.duration_ms ?? "n/a"} ms`;
        setOutput(workflowOutput, JSON.stringify(body, null, 2));
      } catch (error) {
        workflowMeta.textContent = "워크플로우 실행에 실패했습니다.";
        setOutput(workflowOutput, String(error));
      }
    }

    runButton.addEventListener("click", runAgent);
    runWorkflowButton.addEventListener("click", runWorkflow);
    refreshButton.addEventListener("click", refreshCatalog);
    previewGraphButton.addEventListener("click", previewGraph);

    refreshCatalog().catch((error) => {
      setStatus("로딩 실패", "#b53f1d");
      setOutput(resultOutput, String(error));
      resultMeta.textContent = "데모 메타데이터를 불러오지 못했습니다.";
    });
  </script>
</body>
</html>
"""


def demo_html_response() -> HTMLResponse:
    return HTMLResponse(content=DEMO_HTML)
