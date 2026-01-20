import { app } from "../../scripts/app.js";

// node.id(숫자) 혹은 nodeId(문자열) 모두 대응
// DOM 요소(iframe)를 저장
const iframeByNodeId = new Map();

function toAbsUrl(url) {
  try {
    return new URL(url, window.location.origin).toString();
  } catch {
    return url;
  }
}

function extractPreviewUrlFromOutput(output) {
  const ui = output?.ui ?? output ?? null;
  if (!ui) return null;

  // 1) ui_render_url에서 URL 추출
  const sup = ui?.ui_render_url ?? ui?.save_ui_preview;
  if (typeof sup === "string" && sup.length) return sup;
  if (sup && typeof sup === "object" && !Array.isArray(sup)) {
    const u = sup.url;
    if (typeof u === "string" && u.length) return u;
  }
  if (Array.isArray(sup) && sup.length) {
    const first = sup[0];
    if (typeof first === "string" && first.length) return first;
    if (first && typeof first === "object" && typeof first.url === "string" && first.url.length) return first.url;
  }

  // 2) text에서 Preview 라인 파싱
  const textTuple = ui?.text;
  const text = Array.isArray(textTuple) ? String(textTuple[0] ?? "") : (typeof textTuple === "string" ? textTuple : "");
  const m = text.match(/^\s*Preview:\s*(\/view\?[^\s]+)\s*$/m);
  if (m && m[1]) return m[1];

  return null;
}

// 줌 컨트롤 등을 포함한 헤더 생성 함수
function createHeader(contentScale, updateScaleCallback, onResetCallback) {
    const header = document.createElement("div");
    Object.assign(header.style, {
        height: "30px",
        background: "#333",
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        padding: "0 10px",
        borderBottom: "1px solid #444",
        pointerEvents: "auto",
        gap: "8px"
    });

    const zoomLabel = document.createElement("span");
    zoomLabel.textContent = `${Math.round(contentScale * 100)}%`;
    zoomLabel.style.color = "#ccc";
    zoomLabel.style.fontSize = "12px";
    zoomLabel.style.minWidth = "35px";
    zoomLabel.style.textAlign = "center";

    const btnStyle = {
        background: "#555",
        color: "#fff",
        border: "none",
        borderRadius: "4px",
        width: "24px",
        height: "20px",
        cursor: "pointer",
        fontSize: "14px",
        lineHeight: "18px",
        textAlign: "center"
    };

    const zoomOutBtn = document.createElement("button");
    Object.assign(zoomOutBtn.style, btnStyle);
    zoomOutBtn.textContent = "-";
    zoomOutBtn.onclick = (e) => {
        e.stopPropagation();
        updateScaleCallback(-0.1);
        zoomLabel.textContent = `${Math.round(contentScale * 100)}%`;
    };

    const zoomInBtn = document.createElement("button");
    Object.assign(zoomInBtn.style, btnStyle);
    zoomInBtn.textContent = "+";
    zoomInBtn.onclick = (e) => {
        e.stopPropagation();
        updateScaleCallback(0.1);
        zoomLabel.textContent = `${Math.round(contentScale * 100)}%`;
    };

    const resetBtn = document.createElement("button");
    Object.assign(resetBtn.style, btnStyle);
    resetBtn.style.width = "auto";
    resetBtn.style.padding = "0 5px";
    resetBtn.style.fontSize = "11px";
    resetBtn.textContent = "R";
    resetBtn.onclick = (e) => {
        e.stopPropagation();
        onResetCallback();
        zoomLabel.textContent = "100%";
    };

    header.appendChild(zoomLabel);
    header.appendChild(zoomOutBtn);
    header.appendChild(resetBtn);
    header.appendChild(zoomInBtn);

    return { header, updateLabel: (s) => zoomLabel.textContent = `${Math.round(s * 100)}%` };
}

const ext = {
  name: "genui_ui_render",
  async setup() {
    console.log("[UIRender] Extension Loaded");
    // installExecutedListenerOnce(); // 더 이상 전역 리스너 사용 안함
  },
  async nodeCreated(node) {
    if (node.comfyClass !== "UIRender" && node.comfyClass !== "SaveUIPreview") return;

    let contentScale = 1.0;
    
    // 1. iframe 생성
    const iframe = document.createElement("iframe");
    Object.assign(iframe.style, {
        width: "100%",
        height: "100%",
        border: "0",
        backgroundColor: "#222",
        display: "block",
        transformOrigin: "0 0"
    });
    iframe.srcdoc = `
      <style>
        body { display: flex; justify-content: center; align-items: center; height: 100%; margin: 0; color: #888; font-family: sans-serif; background: #222; text-align: center; font-size: 14px; }
      </style>
      <body><div><p>UI Preview Area</p><p style="font-size:12px; opacity:0.7">Run the workflow to see result</p></div></body>
    `;

    // 2. 줌 조절 로직
    const updateContentScale = () => {
        iframe.style.transform = `scale(${contentScale})`;
        iframe.style.width = `${100 / contentScale}%`;
        iframe.style.height = `${100 / contentScale}%`;
    };

    const updateScaleCallback = (delta) => {
        contentScale = Math.max(0.1, Math.min(5.0, contentScale + delta));
        updateContentScale();
    };
    
    const onResetCallback = () => {
        contentScale = 1.0;
        updateContentScale();
    };

    // 3. 컨테이너 생성
    const container = document.createElement("div");
    Object.assign(container.style, {
      position: "absolute",
      overflow: "hidden",
      zIndex: 1, 
      pointerEvents: "none", 
      display: "none",
      borderRadius: "10px",
      boxShadow: "2px 2px 10px rgba(0,0,0,0.5)",
      border: "1px solid #333",
      background: "#222",
      width: "500px", 
      height: "300px",
      flexDirection: "column"
    });
    
    // 헤더 추가
    const { header, updateLabel } = createHeader(contentScale, (d) => {
        updateScaleCallback(d);
        updateLabel(contentScale);
    }, () => {
        onResetCallback();
        updateLabel(contentScale);
    });
    
    // 메인 요소 래퍼
    const wrapper = document.createElement("div");
    Object.assign(wrapper.style, {
        flex: "1",
        width: "100%",
        height: "100%",
        overflow: "hidden", 
        pointerEvents: "auto",
        position: "relative"
    });
    wrapper.appendChild(iframe);

    container.appendChild(header);
    container.appendChild(wrapper);
    document.body.appendChild(container);

    iframeByNodeId.set(node.id, iframe);
    iframeByNodeId.set(String(node.id), iframe);

    // 4. 위치 동기화 루프
    const updatePosition = () => {
        if (!node.graph || !app.canvas) {
            container.style.display = "none";
            return;
        }
        if (node.flags.collapsed) {
             container.style.display = "none";
             return;
        }

        const ds = app.canvas.ds;
        const scale = ds.scale;
        const offset = ds.offset;

        // 노드 우측에 패널 배치
        const gap = 10;
        const panelX = node.pos[0] + node.size[0] + gap;
        const panelY = node.pos[1];
        const panelW = 500;
        const panelH = Math.max(80, node.size[1]);

        const screenX = (panelX + offset[0]) * scale;
        const screenY = (panelY + offset[1]) * scale;
        const screenW = panelW * scale;
        const screenH = panelH * scale;

        const viewportW = window.innerWidth;
        const viewportH = window.innerHeight;

        if (screenX > viewportW || screenY > viewportH || (screenX + screenW) < 0 || (screenY + screenH) < 0) {
            container.style.display = "none";
        } else {
            container.style.display = "flex";
            container.style.transformOrigin = "0 0";
            container.style.left = screenX + "px";
            container.style.top = screenY + "px";
            container.style.width = screenW + "px";
            container.style.height = screenH + "px";
            container.style.transform = "none";
        }

        requestAnimationFrame(updatePosition);
    };

    requestAnimationFrame(updatePosition);

    // 5. 실행 완료 리스너
    const originalOnExecuted = node.onExecuted;
    node.onExecuted = function(data) {
        // URL 추출 및 iframe 업데이트
        const url = extractPreviewUrlFromOutput(data);
        if (url) {
            iframe.removeAttribute("srcdoc");
            iframe.src = toAbsUrl(url);
            iframe.style.backgroundColor = "#fff";
        }
        
        if (originalOnExecuted) originalOnExecuted.apply(this, arguments);
    };

    const originalOnRemoved = node.onRemoved;
    node.onRemoved = function() {
        container.remove();
        iframeByNodeId.delete(node.id);
        iframeByNodeId.delete(String(node.id));
        if (originalOnRemoved) originalOnRemoved.apply(this, arguments);
    };
  }
};

app.registerExtension(ext);
