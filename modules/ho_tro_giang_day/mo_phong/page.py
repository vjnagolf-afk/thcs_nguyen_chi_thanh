# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/mo_phong/page.py
Nhiệm vụ: Phòng Thí nghiệm Ảo (Interactive Simulations) kết hợp Trợ giảng AI.
Chức năng: 
1. Mô phỏng các hiện tượng Khoa học & Toán học tương tác trực quan (Vật lý, Toán học).
2. Tích hợp Trợ giảng AI sử dụng `google-genai` để giải thích hiện tượng và hỗ trợ tư duy.
============================================================
"""

import logging
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

logger = logging.getLogger(__name__)

# Thử import thư viện google-genai mới nhất cho phần Chatbot
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

def render_xd_mo_phong(ai_engine_cu=None):
    st.markdown("### 🧪 Phòng Thí nghiệm Ảo & Trợ lý Mô phỏng Khoa học")
    st.info("💡 **Góc chuyên gia:** Kết hợp giữa Mô hình toán học trực quan (Interactive Simulations) và Trợ giảng AI. Giúp học sinh thay đổi thông số, quan sát đồ thị trực tiếp và đặt câu hỏi cho AI để hiểu sâu bản chất.")

    # Tạo 2 Tabs chính cho phân hệ Mô phỏng
    tab_sim, tab_chat = st.tabs(["🔬 1. Mô phỏng Thí nghiệm & Đồ thị (Interactive Lab)", "🤖 2. Trợ giảng AI Giải đáp Thí nghiệm"])

    # ========================================================
    # TAB 1: MÔ PHỎNG KHOA HỌC & TOÁN HỌC (INTERACTIVE SIMULATION)
    # ========================================================
    with tab_sim:
        st.markdown("#### Chọn Mô hình Thí nghiệm Ảo")
        chon_mo_hinh = st.selectbox(
            "Chọn chủ đề mô phỏng:",
            [
                "🚀 Chuyển động Ném ngang (Vật lý 10)",
                "⚡ Định luật Ohm & Mạch điện cơ bản (Vật lý 9/11)",
                "📈 Khảo sát hàm số bậc 2: $y = ax^2 + bx + c$ (Toán học)"
            ]
        )

        st.markdown("---")

        if "Ném ngang" in chon_mo_hinh:
            col_ctrl, col_view = st.columns([1, 2])
            with col_ctrl:
                st.markdown("##### 🎛️ Thông số đầu vào")
                v0 = st.slider("Vận tốc ban đầu $v_0$ (m/s):", 1.0, 50.0, 15.0, 1.0)
                h0 = st.slider("Độ cao ban đầu $h$ (m):", 5.0, 100.0, 45.0, 5.0)
                g = 9.81

            with col_view:
                st.markdown("##### 📊 Mô phỏng quỹ đạo bay")
                # Tính toán vật lý
                t_flight = np.sqrt(2 * h0 / g)
                t = np.linspace(0, t_flight, 100)
                x = v0 * t
                y = h0 - 0.5 * g * t**2

                df_sim = pd.DataFrame({"Khoảng cách X (m)": x, "Độ cao Y (m)": y})
                fig = px.line(df_sim, x="Khoảng cách X (m)", y="Độ cao Y (m)", title=f"Quỹ đạo ném ngang (Thời gian bay: {t_flight:.2f}s)")
                fig.update_yaxes(rangemode="tozero")
                st.plotly_chart(fig, use_container_width=True)
                st.success(f"🎯 Tầm bay xa tối đa đạt được: **{x[-1]:.2f} mét**")

        elif "Định luật Ohm" in chon_mo_hinh:
            col_ctrl, col_view = st.columns([1, 2])
            with col_ctrl:
                st.markdown("##### 🎛️ Thông số mạch điện")
                u = st.slider("Hiệu điện thế $U$ (Volt):", 1.0, 220.0, 12.0, 1.0)
                r = st.slider("Điện trở $R$ ($\Omega$):", 1.0, 100.0, 10.0, 1.0)
            with col_view:
                st.markdown("##### 📊 Định luật Ohm ($I = \\frac{U}{R}$)")
                i_val = u / r
                st.metric(label="Cường độ dòng điện $I$ (Ampere)", value=f"{i_val:.2f} A")
                
                # Vẽ đồ thị quan hệ I theo U (khi R cố định)
                u_range = np.linspace(0, 220, 50)
                i_range = u_range / r
                df_ohm = pd.DataFrame({"Hiệu điện thế U (V)": u_range, "Dòng điện I (A)": i_range})
                fig = px.line(df_ohm, x="Hiệu điện thế U (V)", y="Dòng điện I (A)", title=f"Đặc tuyến V-I với điện trở R = {r}Ω")
                st.plotly_chart(fig, use_container_width=True)

        else: # Khảo sát hàm số bậc 2
            col_ctrl, col_view = st.columns([1, 2])
            with col_ctrl:
                st.markdown("##### 🎛️ Hệ số hàm số")
                a = st.slider("Hệ số a:", -5.0, 5.0, 1.0, 0.5)
                b = st.slider("Hệ số b:", -10.0, 10.0, 0.0, 1.0)
                c = st.slider("Hệ số c:", -10.0, 10.0, 0.0, 1.0)
            with col_view:
                st.markdown("##### 📊 Đồ thị Parabol")
                x = np.linspace(-10, 10, 200)
                y = a * x**2 + b * x + c
                df_math = pd.DataFrame({"x": x, "y": y})
                fig = px.line(df_math, x="x", y="y", title=f"Đồ thị y = {a}x² + {b}x + {c}")
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.add_vline(x=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
                
                delta = b**2 - 4*a*c
                st.info(f"📌 Delta ($\Delta$): **{delta}** | Tọa độ đỉnh $I\\left(\\frac{-b}{2a}, \\frac{-\\Delta}{4a}\\right)$")

    # ========================================================
    # TAB 2: TRỢ GIẢNG AI MÔ PHỎNG (CHATBOT GOOGLE-GENAI)
    # ========================================================
    with tab_chat:
        st.markdown("#### Trợ giảng AI giải thích hiện tượng mô phỏng")
        
        # Sidebar cấu hình riêng cho phần Chat trong tab này
        with st.sidebar:
            st.markdown("---")
            st.markdown("### ⚙️ Cài đặt Trợ giảng AI")
            api_key_input = st.text_input("Gemini API Key (Tùy chọn mô phỏng):", type="password", placeholder="AIzaSy...")
            che_do_su_pham = st.radio(
                "Chế độ phản hồi:",
                [
                    "💡 Gợi mở tư duy (Socratic) - Không giải hộ, gợi ý từng bước.",
                    "📚 Giải thích chi tiết khoa học - Cặn kẽ, rõ ràng bản chất."
                ],
                key="chat_mode_sim"
            )
            if st.button("🧹 Xóa lịch sử chat", use_container_width=True, key="clear_sim_chat"):
                st.session_state["sim_chatbot_messages"] = []
                st.rerun()

        if "sim_chatbot_messages" not in st.session_state:
            st.session_state["sim_chatbot_messages"] = [
                {
                    "role": "assistant", 
                    "content": "👋 Chào bạn! Mình là Trợ giảng AI chuyên trách phòng thí nghiệm ảo. Bạn có thắc mắc gì về các công thức vật lý, toán học hay hiện tượng vừa mô phỏng không?"
                }
            ]

        if "Gợi mở" in che_do_su_pham:
            system_instruction = "Bạn là trợ giảng ân cần. Không giải bài hộ hoàn toàn, hãy đưa ra câu hỏi gợi mở, hướng dẫn từng bước để học sinh tự tư duy khoa học."
        else:
            system_instruction = "Bạn là chuyên gia khoa học giáo dục. Hãy giải thích hiện tượng thí nghiệm, công thức toán lý một cách chi tiết, dễ hiểu, kèm ví dụ thực tế."

        chat_container = st.container(height=400, border=True)
        
        with chat_container:
            for message in st.session_state["sim_chatbot_messages"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Hỏi AI về hiện tượng mô phỏng..."):
            st.session_state["sim_chatbot_messages"].append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Trợ giảng đang phân tích..."):
                        try:
                            if genai is None:
                                st.error("❌ Thư viện `google-genai` chưa được cài đặt.")
                                return

                            client_kwargs = {}
                            if api_key_input.strip():
                                client_kwargs["api_key"] = api_key_input.strip()
                            
                            client = genai.Client(**client_kwargs)
                            model_id = "gemini-2.5-flash"
                            
                            config = types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7,
                            )
                            
                            formatted_contents = []
                            for m in st.session_state["sim_chatbot_messages"]:
                                role_name = "user" if m["role"] == "user" else "model"
                                formatted_contents.append(
                                    types.Content(
                                        role=role_name,
                                        parts=[types.Part.from_text(text=m["content"])]
                                    )
                                )
                            
                            response = client.models.generate_content(
                                model=model_id,
                                contents=formatted_contents,
                                config=config
                            )
                            
                            reply_text = response.text
                            st.markdown(reply_text)
                            st.session_state["sim_chatbot_messages"].append({"role": "assistant", "content": reply_text})
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi kết nối Google GenAI SDK: {e}")

# Tương thích với cấu trúc gọi hàm render của hệ thống
def render_xd_ca_nhan_hoa(ai_engine_cu=None):
    render_xd_mo_phong(ai_engine_cu)
