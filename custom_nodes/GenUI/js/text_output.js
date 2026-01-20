import { app } from "../../scripts/app.js";

// TextOutput 노드의 DOM 요소(textarea) 관리
const elementByNodeId = new Map();

// 줌 컨트롤 헤더 생성 함수 (TextOutput용)
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
  name: "genui_text_output",
  async setup() {
    // 필요한 경우 전역 리스너 등록
  },
  async nodeCreated(node) {
    if (node.comfyClass !== "TextOutput") return;

    let contentScale = 1.0;
    
    // 1. 메인 요소(Textarea) 생성
    const mainElement = document.createElement("textarea");
    Object.assign(mainElement.style, {
        width: "100%",
        height: "100%",
        border: "0",
        backgroundColor: "#222",
        color: "#ddd",
        padding: "10px",
        boxSizing: "border-box",
        resize: "none",
        outline: "none",
        fontSize: "12px",
        lineHeight: "1.5",
        fontFamily: "monospace",
        whiteSpace: "pre-wrap",
        overflowY: "auto",
        display: "block",
        transformOrigin: "0 0"
    });
    mainElement.readOnly = true;
    mainElement.value = "Waiting for output...";

    // 2. 줌 조절 로직
    const updateContentScale = () => {
        mainElement.style.transform = `scale(${contentScale})`;
        mainElement.style.width = `${100 / contentScale}%`;
        mainElement.style.height = `${100 / contentScale}%`;
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
      width: "400px", 
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
    wrapper.appendChild(mainElement);

    container.appendChild(header);
    container.appendChild(wrapper);
    document.body.appendChild(container);

    elementByNodeId.set(node.id, mainElement);

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

        // 노드 위에 오버레이
        const targetX = node.pos[0];
        // 타이틀바(약 30px) 아래부터 시작
        const targetY = node.pos[1] + 30; 
        const targetW = node.size[0];
        const targetH = node.size[1] - 30;

        const screenX = (targetX + offset[0]) * scale;
        const screenY = (targetY + offset[1]) * scale;
        const screenW = targetW * scale;
        const screenH = targetH * scale;

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
        if (data && data.text) {
             const text = data.text[0];
             mainElement.value = text;
        }
        if (originalOnExecuted) originalOnExecuted.apply(this, arguments);
    };
    
    // 6. 노드 크기 초기화
    if (!node._sizeInitialized) {
        node.setSize([400, 300]);
        node._sizeInitialized = true;
    }

    const originalOnRemoved = node.onRemoved;
    node.onRemoved = function() {
        container.remove();
        elementByNodeId.delete(node.id);
        if (originalOnRemoved) originalOnRemoved.apply(this, arguments);
    };
  }
};

app.registerExtension(ext);

