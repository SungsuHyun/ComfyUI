import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
	name: "GenUI.ToolCollection",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		// 1. ToolCollection 노드 가변 입력 설정
		if (nodeData.name === "ToolCollection") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				this.addWidget("button", "+ Add Tool", null, () => {
					let count = 1;
					if (this.inputs) {
						for (const input of this.inputs) {
							if (input.name.startsWith("tool_")) {
								const num = parseInt(input.name.split("_")[1]);
								if (!isNaN(num) && num >= count) count = num + 1;
							}
						}
					}
					const name = `tool_${count}`;
					this.addInput(name, "TOOL");
				});
				return r;
			};
		}

		// 2. ReadTextFileTool 파일 업로드 버튼 추가
		if (nodeData.name === "ReadTextFileTool") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				// 'file' 위젯 찾기
				const fileWidget = this.widgets.find(w => w.name === "file");
				if (fileWidget) {
					// 업로드 버튼 추가
					const uploadWidget = this.addWidget("button", "Choose file to upload", null, () => {
						const input = document.createElement("input");
						input.type = "file";
						input.accept = ".txt,.json,.csv,.log,.md";
						input.onchange = async () => {
							if (input.files.length > 0) {
								const file = input.files[0];
								const formData = new FormData();
								formData.append("image", file); // ComfyUI API는 'image' 필드로 파일을 받음
								formData.append("overwrite", "true");
								
								try {
									const resp = await api.fetchApi("/upload/image", {
										method: "POST",
										body: formData,
									});
									
									if (resp.status === 200) {
										const data = await resp.json();
										// 업로드 성공 시 드롭다운 값을 해당 파일로 변경
										fileWidget.value = data.name;
										if (fileWidget.callback) fileWidget.callback(data.name);
									}
								} catch (error) {
									console.error("File upload error:", error);
								}
							}
						};
						input.click();
					});
				}
				return r;
			};
		}
	},
});
