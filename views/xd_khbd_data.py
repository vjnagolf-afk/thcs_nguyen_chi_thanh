# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (TÍCH HỢP TỰ ĐỘNG OCR VISION)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import pandas as pd
from docx import Document
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)

NLS_GV_VAN_BAN_MAC_DINH = "Thông tư 18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tu_dong": "Tự động soạn từ SGK",
}

MIN_SOURCE_CHARS = 100

def init_session_state():
    defaults = {
        "khbd_mode": "tu_dong",
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_processing": False,
        "khbd_nls_noi_dung": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_ket_qua():
    st.session_state["khbd_result"] = None

def reset_toan_bo_khbd():
    st.session_state["khbd_result"] = None
    st.session_state["khbd_nls_list"] = []
    st.session_state["khbd_hoat_dong_list"] = []
    st.session_state["khbd_nls_noi_dung"] = ""
    st.session_state["khbd_mode"] = "tu_dong"
    st.session_state["khbd_processing"] = False

def set_mode(mode: str):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    st.session_state.khbd_mode = mode

# ============================================================
# TỪ ĐIỂN KHUNG NĂNG LỰC SỐ (Theo Thông tư 18/2026/TT-BGDĐT)
# ============================================================
KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "- Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS).\n- Sử dụng được các công cụ hỗ trợ dạy học trực tuyến để triển khai các phiên học trực tuyến, cung cấp tài liệu học tập và tổ chức các hoạt động dạy học đơn giản.",
            "Thành thạo": "- Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ.\n- Thiết kế và triển khai được các hoạt động dạy học theo mô hình kết hợp (blended learning) hiệu quả.\n- Lựa chọn và áp dụng được các công cụ và tài nguyên số phù hợp với mục tiêu dạy học.\n- Hướng dẫn và triển khai được phương pháp dạy học theo dự án trực tuyến, lớp học đảo ngược trên nền tảng quản lí học tập LMS.",
            "Nâng cao": "- Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số.\n- Hướng dẫn được đồng nghiệp trong việc thiết kế các trải nghiệm học tập số hóa tiên tiến."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "- Sử dụng được các kênh giao tiếp số (email, diễn đàn) để trả lời câu hỏi và hỗ trợ người học khi cần thiết.",
            "Thành thạo": "- Sử dụng được các kênh giao tiếp số (diễn đàn, LMS, nhóm chat...) để tương tác, giải đáp thắc mắc, cung cấp tài liệu hỗ trợ người học.\n- Sử dụng được dữ liệu học tập số để xác định người học cần hỗ trợ và lựa chọn biện pháp can thiệp phù hợp.\n- Thiết lập được các hoạt động, môi trường số cho phép tương tác, hỗ trợ cá nhân hóa và kịp thời cho người học.",
            "Nâng cao": "- Hướng dẫn được đồng nghiệp xây dựng văn hóa hỗ trợ học tập tích cực trên nền tảng số.\n- Sáng tạo, thử nghiệm, phát triển được các công cụ/phương pháp hỗ trợ dạy học thông minh trên nền tảng số."
        },
        "1.3. Cá nhân hóa người học": {
            "Cơ bản": "- Xác định được các nhu cầu, sự khác biệt của người học trong sử dụng công nghệ số.\n- Lựa chọn, điều chỉnh được các công cụ và nội dung số phù hợp với nhu cầu của người học.",
            "Thành thạo": "- Sử dụng được công nghệ số để thiết kế lộ trình học tập linh hoạt, cho phép người học tự chủ về tốc độ, nội dung và cách thức học tập dựa trên nền tảng số.\n- Thiết kế được các nhiệm vụ học tập phân hóa theo trình độ, năng lực và sở thích của người học trong môi trường trực tuyến.\n- Tích hợp đa dạng, linh hoạt các công cụ số hỗ trợ hoạt động học tập thích ứng, điều chỉnh theo kết quả học tập của người học.",
            "Nâng cao": "- Thiết kế được môi trường học tập số cá nhân hóa, cung cấp công cụ cập nhật cho người học tự định hướng, tự điều chỉnh quá trình học tập.\n- Đánh giá được hiệu quả của các chiến lược dạy học cá nhân hóa bằng công nghệ."
        },
        "1.4. Học tập cộng tác": {
            "Cơ bản": "- Sử dụng được công cụ số cơ bản để tổ chức cho người học làm việc nhóm đơn giản.\n- Thiết kế được các nhiệm vụ học tập, chia sẻ tài liệu, ý tưởng trên nền tảng số.",
            "Thành thạo": "- Thiết kế được các nhiệm vụ học tập yêu cầu người học sử dụng đa dạng công cụ số để cùng xây dựng nội dung, kiến thức.\n- Hướng dẫn được người học kĩ năng giao tiếp, hợp tác hiệu quả trong môi trường số.\n- Sử dụng được công nghệ để quản lý và đánh giá hiệu quả làm việc nhóm, đánh giá quá trình và sản phẩm cộng tác của nhóm.",
            "Nâng cao": "- Xây dựng được các dự án cộng tác phức tạp, kết nối người học theo mô hình học tập cộng tác trên nền tảng số.\n- Xây dựng và quản lí được các cộng đồng học tập trực tuyến.\n- Hướng dẫn được đồng nghiệp triển khai học tập cộng tác dựa trên công nghệ số trong nhà trường."
        }
    },
    "2. KIỂM TRA, ĐÁNH GIÁ": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "- Sử dụng được hình thức kiểm tra, đánh giá truyền thống, có thể nhập điểm vào hệ thống số.\n- Áp dụng được một số công cụ tạo bài kiểm tra online đơn giản trong hoạt động dạy học.",
            "Thành thạo": "- Sử dụng được các công cụ số phổ biến để tạo bài kiểm tra, khảo sát nhằm đánh giá quá trình và đánh giá tổng kết.\n- Kết hợp được một số hình thức đánh giá số đơn giản vào quá trình dạy học.\n- Thiết kế và áp dụng được các hình thức đa dạng, công cụ đánh giá số phù hợp với mục tiêu và nội dung học tập.",
            "Nâng cao": "- Sáng tạo triển khai các phương pháp, mô hình đánh giá số tiên tiến, đáp ứng yêu cầu đánh giá năng lực phức hợp.\n- Hướng dẫn được đồng nghiệp xây dựng và áp dụng các chiến lược đánh giá số hiệu quả, công bằng trong nhà trường."
        },
        "2.2. Phân tích kết quả học tập": {
            "Cơ bản": "- Sử dụng được các chức năng cơ bản của LMS/công cụ đánh giá để xem báo cáo về hoạt động, kết quả của người học.",
            "Thành thạo": "- Phân tích được dữ liệu từ các hệ thống đánh giá số để nhận diện quá trình tiến bộ và thành tích học tập của người học.\n- Sử dụng được dữ liệu, công cụ trực quan hóa dữ liệu để xây dựng báo cáo đánh giá sự tiến bộ của người học.\n- Xây dựng được các bảng điều khiển tự động (dashboard) dữ liệu học tập trực quan.",
            "Nâng cao": "- Áp dụng được các kĩ thuật phân tích dữ liệu học tập nâng cao để dự đoán xu hướng, phát hiện sớm các vấn đề và đề xuất can thiệp.\n- Hướng dẫn được đồng nghiệp về cách khai thác và diễn giải dữ liệu để cải tiến dạy học."
        },
        "2.3. Phản hồi và đánh giá cải tiến": {
            "Cơ bản": "- Sử dụng được các chức năng cung cấp phản hồi trên hệ thống LMS.\n- Cung cấp phản hồi kịp thời cho người học bằng văn bản hoặc điểm số thông qua các nền tảng số.",
            "Thành thạo": "- Sử dụng được đa dạng công cụ số (ghi âm, video ngắn, bình luận trực tiếp trên tài liệu) để đưa ra phản hồi chi tiết, kịp thời.\n- Thiết kế được các quy trình phản hồi và đánh giá cải tiến có sự tham gia của người học (tự đánh giá, đánh giá chéo) bằng công nghệ.",
            "Nâng cao": "- Sử dụng được dữ liệu phân tích để điều chỉnh kế hoạch bài dạy, phương pháp và cung cấp nhiệm vụ học tập hỗ trợ cá nhân người học.\n- Hướng dẫn được đồng nghiệp sử dụng phản hồi bằng công cụ số và dữ liệu học tập để cải tiến liên tục chương trình và hoạt động giáo dục."
        }
    },
    "3. TRAO QUYỀN CHO NGƯỜI HỌC": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "- Sử dụng được các công cụ số cơ bản để hỗ trợ người học gặp khó khăn trong học tập.\n- Lựa chọn và sử dụng được các công cụ, tài nguyên số có tính đến sự đa dạng của người học.\n- Đảm bảo mọi người học có cơ hội sử dụng thiết bị, hạ tầng số của nhà trường khi cần thiết.",
            "Thành thạo": "- Khai thác, lựa chọn và điều chỉnh được tài nguyên, đa dạng hóa công cụ số để đáp ứng nhu cầu đặc biệt của người học.\n- Thiết kế được nội dung, tài nguyên số đảm bảo tính tiếp cận và hòa nhập trong môi trường số.",
            "Nâng cao": "- Hướng dẫn được đồng nghiệp về chiến lược và công nghệ số hỗ trợ giáo dục hòa nhập."
        },
        "3.2. Giải quyết vấn đề": {
            "Cơ bản": "- Thiết kế được các nhiệm vụ học tập yêu cầu người học sử dụng Internet để tìm kiếm thông tin để trả lời câu hỏi hoặc giải quyết vấn đề học tập đơn giản.",
            "Thành thạo": "- Thiết kế được các nhiệm vụ dự án học tập yêu cầu người học sử dụng công nghệ số để xác định vấn đề, thu thập, phân tích thông tin và đề xuất giải pháp.\n- Tổ chức được các hoạt động học tập dựa trên vấn đề (problem-based) hoặc dự án (project-based) phức tạp, trong đó công nghệ số là công cụ thiết yếu để nghiên cứu, hợp tác và tạo ra sản phẩm.",
            "Nâng cao": "- Hướng dẫn được đồng nghiệp xây dựng hệ sinh thái học tập số, kết nối người học với các chuyên gia và vấn đề thực tiễn bên ngoài nhà trường để giải quyết các vấn đề thực tế của cộng đồng."
        },
        "3.3. Khuyến khích sự tham gia tích cực của người học": {
            "Cơ bản": "- Sáng tạo và điều phối tương tác số đơn giản để thu hút sự chú ý và khuyến khích người học tham gia vào hoạt động học tập.\n- Tích hợp được công nghệ số trong dạy học nhằm trực quan hóa và tăng hiệu quả trình bày nội dung dạy học.",
            "Thành thạo": "- Tích hợp được các yếu tố trò chơi hóa, tương tác và các công cụ sáng tạo nội dung để thúc đẩy người học chủ động, tích cực tham gia vào bài học.\n- Thiết kế được hoạt động khuyến khích người học tự tạo ra nội dung số, chia sẻ kiến thức thông qua các nền tảng số, giải quyết vấn đề bằng mô phỏng, thí nghiệm ảo, thực tế ảo, thực tế ảo tăng cường.",
            "Nâng cao": "- Sử dụng được các công cụ thiết kế môi trường học tập số năng động, lấy người học làm trung tâm.\n- Hướng dẫn được đồng nghiệp sáng tạo triển khai các hoạt động học tập tích cực bằng công nghệ số."
        }
    },
    "4. KĨ NĂNG CÔNG NGHỆ SỐ": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "- Sử dụng được công cụ tìm kiếm để tìm thông tin, tài liệu phục vụ bài giảng.\n- Lưu trữ và sắp xếp một cách khoa học các dữ liệu trên máy tính hoặc đám mây.",
            "Thành thạo": "- Đánh giá được độ tin cậy của nguồn tin trên Internet, mạng xã hội.\n- Sử dụng được các kĩ thuật tìm kiếm nâng cao.\n- Hướng dẫn được người học các kĩ năng tư duy phản biện khi tìm kiếm, xử lí, tiếp nhận thông tin số từ các nguồn khác nhau.\n- Tổ chức được các nhiệm vụ học tập nâng cao cho phép người học chủ động tìm kiếm và xử lí thông tin trong môi trường số.",
            "Nâng cao": "- Sử dụng được công cụ để thu thập và trực quan hóa dữ liệu đơn giản, phân tích và đánh giá độ tin cậy của thông tin trong quá trình dạy học.\n- Hướng dẫn được đồng nghiệp tích hợp phát triển năng lực thông tin vào chương trình dạy học."
        },
        "4.2. Sáng tạo nội dung số": {
            "Cơ bản": "- Sử dụng được các công cụ số phổ biến để tạo nội dung dạy học theo định dạng số khác nhau.\n- Tích hợp được các định dạng số trong nội dung thực hiện nhiệm vụ của người học.",
            "Thành thạo": "- Tích hợp được công nghệ số trong hoạt động sáng tạo nội dung số, xây dựng kho học liệu số.\n- Hướng dẫn được người học sử dụng các công cụ cơ bản để tạo nội dung số, thực hiện quyền tác giả, giấy phép, cách trích dẫn, sử dụng và chia sẻ tài nguyên số hợp pháp.\n- Sử dụng được nền tảng, công cụ số đa dạng để tạo và chia sẻ nội dung hợp lệ.",
            "Nâng cao": "- Sử dụng thành thạo các công cụ chuyên dụng để tạo ra các học liệu số có tính tương tác cao.\n- Hướng dẫn được đồng nghiệp phát triển nền tảng học tập tích hợp AI, thực tế ảo, thực tế ảo tăng cường trong sáng tạo nội dung số vào các môn học."
        },
        "4.3. An toàn": {
            "Cơ bản": "- Có hiểu biết về bảo vệ sức khỏe thể chất, tinh thần, đảm bảo an sinh số trong hoạt động dạy học.\n- Bố trí, sắp xếp được không gian, thời gian sử dụng thiết bị, công cụ số hợp lí cho người học.\n- Nhận diện và xử lí được các tình huống bắt nạt trực tuyến.",
            "Thành thạo": "- Tích hợp được kiến thức, kĩ năng nhận diện và phòng tránh các rủi ro phổ biến trên mạng trong quá trình dạy học.\n- Áp dụng được các biện pháp bảo vệ dữ liệu cá nhân và của người học.\n- Thực hiện được các biện pháp cơ bản đảm bảo an toàn thiết bị, tài khoản trong lớp học và hướng dẫn người học cách bảo vệ dữ liệu cá nhân, định danh số, quản lí dấu vết số.",
            "Nâng cao": "- Thực hiện được các biện pháp đảm bảo an toàn sức khỏe, áp dụng các phương pháp dạy học giảm căng thẳng trong môi trường số cho người học.\n- Cập nhật và phổ biến các xu hướng, mối đe dọa mới và cách phòng chống cho cộng đồng giáo viên, phụ huynh.\n- Hướng dẫn được đồng nghiệp xây dựng môi trường học tập số an toàn, lành mạnh trong lớp học và nhà trường."
        }
    },
    "5. PHÁT TRIỂN CHUYÊN MÔN": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "- Sử dụng được email, nhóm chat của trường/tổ để trao đổi thông tin công việc và giao tiếp với phụ huynh.",
            "Thành thạo": "- Sử dụng hiệu quả các kênh giao tiếp số chính thức của trường để tương tác với các bên liên quan, phù hợp với từng đối tượng và mục đích giáo dục.\n- Sử dụng được công cụ số cơ bản để giao tiếp, chia sẻ thông tin, dữ liệu và tham gia hoạt động chuyên môn với đồng nghiệp.",
            "Nâng cao": "- Xây dựng và quản lí được chiến lược truyền thông số, các kênh truyền thông số chính thức của trường để chia sẻ và kết nối cộng đồng.\n- Hướng dẫn được đồng nghiệp đổi mới cách thức giao tiếp trong tổ chức bằng công nghệ số tăng cường tính minh bạch, sự tham gia của các bên liên quan."
        },
        "5.2. Hợp tác phát triển chuyên môn": {
            "Cơ bản": "- Chủ động tham gia các cộng đồng học tập trực tuyến.\n- Tự đánh giá được khó khăn, thách thức và thuận lợi ứng dụng công nghệ số trong công việc.",
            "Thành thạo": "- Xây dựng được kế hoạch cải tiến, đổi mới ứng dụng công nghệ số trong hoạt động chuyên môn.\n- Chủ động tìm kiếm và tham gia các khóa học cơ bản để cập nhật kiến thức, kĩ năng số.\n- Tự đánh giá, cải tiến ứng dụng công nghệ số trong dạy học trong môi trường số.\n- Tham gia chia sẻ, học tập và cập nhật kĩ năng ứng dụng công nghệ số với đồng nghiệp.",
            "Nâng cao": "- Cập nhật được các xu hướng công nghệ và phương pháp sư phạm số mới, áp dụng kiến thức, kĩ năng số vào thực tiễn dạy học.\n- Hướng dẫn được đồng nghiệp xây dựng các yêu cầu về dạy học trong môi trường số, phát triển các công cụ, phương pháp hỗ trợ tự phản ánh về năng lực số."
        },
        "5.3. Phát triển, sử dụng, chia sẻ và quản lí học liệu số": {
            "Cơ bản": "- Sử dụng được các công cụ tìm kiếm phổ biến để tìm kiếm tài nguyên, kho học liệu số, thư viện trực tuyến, tài nguyên giáo dục mở (OER).\n- Lựa chọn được tài nguyên phù hợp với mục tiêu bài học.",
            "Thành thạo": "- Lựa chọn và sử dụng được tài nguyên, học liệu số phù hợp với đối tượng đa dạng của người học.\n- Tạo được tài nguyên số phục vụ cho môn học dựa từ các nguồn có sẵn.\n- Tổ chức lưu trữ, quản lí và chia sẻ được kho học liệu số cá nhân một cách khoa học, an toàn.\n- Đánh giá được chất lượng, độ tin cậy, tính pháp lí và sư phạm của tài nguyên, học liệu số.",
            "Nâng cao": "- Xây dựng và quản trị được các hệ thống quản lí, chia sẻ tài nguyên số cho tổ/trường.\n- Hướng dẫn được đồng nghiệp xây dựng và quản trị kho học liệu số mở của nhà trường."
        }
    },
    "6. ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "- Nhận diện được cách vận hành của AI và các công nghệ có tích hợp AI.",
            "Thành thạo": "- Thiết kế được các hoạt động dạy học tích hợp AI một cách sáng tạo và có trách nhiệm.",
            "Nâng cao": "- Triển khai đổi mới phương pháp dạy học mới có tích hợp sâu AI đáp ứng cá nhân hóa và dạy học thích ứng.\n- Hướng dẫn, lựa chọn và đề xuất sử dụng các công cụ AI phù hợp cho đồng nghiệp."
        },
        "6.2. Đạo đức AI": {
            "Cơ bản": "- Nhận diện được các khả năng tích hợp sử dụng AI trong hỗ trợ hoạt động dạy học.\n- Sử dụng được các công cụ AI đơn giản (chủ yếu là AI tạo sinh) để hỗ trợ dạy học và kiểm tra đánh giá.\n- Nhận diện được khả năng thu thập dữ liệu và thông tin cá nhân khi sử dụng công cụ AI, những tiềm ẩn rủi ro khi sử dụng AI không đúng cách.\n- Thể hiện sự cẩn trọng và có trách nhiệm đối với quyền riêng tư của người học, có trách nhiệm khi sử dụng công cụ AI trong dạy học, kiểm tra đánh giá.\n- Thiết kế các hoạt động giáo dục tích hợp AI, cân bằng giữa tương tác công nghệ và tương tác xã hội, phát triển tư duy phản biện.",
            "Thành thạo": "- Khai thác hiệu quả các công cụ AI chuyên biệt cho giáo dục để tạo học liệu số tương tác đa dạng, cá nhân hóa một phần nội dung/bài tập, hỗ trợ chấm điểm tự động.\n- Hướng dẫn được người học sử dụng AI có trách nhiệm, nhận biết ưu/nhược điểm và các rủi ro liên quan khi sử dụng AI.\n- Thực hiện được các biện pháp cần thiết phòng ngừa rủi ro và về các vấn đề đạo đức cơ bản khi sử dụng AI.\n- Lựa chọn, đánh giá được các ứng dụng AI dựa trên tiêu chí về đạo đức, chính sách bảo mật, sự công bằng trong tiếp cận và tác động khác trong dạy học, kiểm tra đánh giá.\n- Thiết kế và tích hợp hoạt động hướng dẫn người học sử dụng AI an toàn và có đạo đức trong hoạt động học tập.",
            "Nâng cao": "- Đánh giá được ưu/nhược điểm và các vấn đề đạo đức của công cụ AI trong giáo dục, cập nhật, hướng dẫn và chia sẻ với đồng nghiệp các vấn đề về đạo đức sử dụng AI.\n- Tham gia xây dựng chính sách, hướng dẫn về sử dụng AI có đạo đức trong nhà trường."
        },
        "6.3. Sư phạm AI": {
            "Cơ bản": "- Nhận diện được khả năng tích hợp AI theo hướng cá nhân hóa và lấy người học làm trung tâm.\n- Có hiểu biết về lợi ích sư phạm của công cụ AI để hỗ trợ dạy học.",
            "Thành thạo": "- Ứng dụng được công cụ AI linh hoạt trong các bước dạy học đảm bảo nguyên tắc lấy người học làm trung tâm, giáo dục hòa nhập.\n- Lựa chọn và ứng dụng được các hệ thống, công cụ AI phù hợp, giảm thiểu rủi ro trong thiết kế dạy học, kiểm tra đánh giá.\n- Tổ chức và quản lý được hoạt động tương tác 3 chiều giữa giáo viên, người học với các công cụ AI trong dạy học.",
            "Nâng cao": "- Xây dựng được nguyên tắc sư phạm sử dụng AI trong hoạt động dạy học.\n- Hướng dẫn được đồng nghiệp thiết kế và sử dụng AI theo tiếp cận đồng sáng tạo, lấy con người làm trung tâm trong các hoạt động sư phạm."
        },
        "6.4. AI cho phát triển chuyên môn": {
            "Cơ bản": "- Nhận diện được sự cân bằng giữa vai trò của người giáo viên và nhiệm vụ phát triển năng lực số, năng lực AI trong dạy học.\n- Sử dụng được công cụ AI phù hợp để lập kế hoạch, theo dõi và phân tích quá trình phát triển chuyên môn của bản thân.",
            "Thành thạo": "- Sử dụng được các công cụ AI đơn giản (chủ yếu là AI tạo sinh) để hỗ trợ học tập suốt đời và phát triển chuyên môn nghiệp vụ bản thân.\n- Đề xuất được các hướng sử dụng hiệu quả các nền tảng AI để tìm kiếm tài nguyên, tham gia cộng đồng thực hành hỗ trợ phát triển bản thân.\n- Đánh giá được các rủi ro đạo đức từ các nền tảng AI và triển khai các biện pháp phòng ngừa giảm thiểu tác động tiêu cực.",
            "Nâng cao": "- Hướng dẫn đổi mới sáng tạo cho đồng nghiệp dựa trên các nền tảng AI phù hợp và tiếp cận sư phạm số.\n- Xây dựng hoặc sử dụng được các bộ công cụ AI tạo sinh hỗ trợ phát triển chuyên môn của đồng nghiệp."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {
            "Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản.",
            "Mức 2": "Biết đánh giá độ tin cậy của thông tin."
        }
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {
            "Mức 1": "Biết sử dụng email, chat để trao đổi học tập.",
            "Mức 2": "Biết sử dụng nền tảng làm việc nhóm (Padlet, Azota...)."
        }
    }
}

def get_nls_framework(loai_khung):
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def get_nls_domains(loai_khung):
    return list(get_nls_framework(loai_khung).keys())

def get_nls_components(loai_khung, linh_vuc):
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())

def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())

def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do):
    try:
        return get_nls_framework(loai_khung)[linh_vuc][thanh_phan][muc_do]
    except Exception:
        return ""

def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return

    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "Khung DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list:
        st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.khbd_nls_list
    if not items: return "Không yêu cầu tích hợp Năng lực số chuyên biệt."
    result = []
    for index, item in enumerate(items, start=1):
        result.append(f"{index}. Mục tiêu NLS: {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}):\n{item['noi_dung']}")
    return "\n".join(result)

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    if chars == 0:
        return {"status": "empty", "message": f"Không đọc được nội dung chữ từ {source_name}. Nếu là PDF scan dạng ảnh, hệ thống tự động kích hoạt tính năng đọc bằng mắt AI (Vision OCR) để bảo toàn công thức Toán/Lý.", "chars": chars, "words": words}
    if chars < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} quá ngắn, không đủ cơ sở để sinh giáo án dài.", "chars": chars, "words": words}
    return {"status": "valid", "message": f"{source_name} đủ dữ liệu.", "chars": chars, "words": words}

# ============================================================
# CƠ CHẾ ĐỌC FILE TỰ ĐỘNG OCR BẰNG GEMINI 2.5 FLASH VISION
# ============================================================
def extract_text_via_gemini_ocr(file_bytes, file_name="document.pdf"):
    """
    Sử dụng Gemini File API để đọc trực tiếp file PDF Scan / Ảnh,
    giữ nguyên vẹn định dạng, công thức Toán học (LaTeX) và Bảng biểu (Markdown).
    """
    import tempfile
    import os
    import time
    try:
        import google.generativeai as genai
    except ImportError:
        return ""

    # Lấy API key từ session state đã đăng nhập
    api_key = st.session_state.get("user_api_key")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
            
    if not api_key:
        return "❌ Cần nhập API Key để dùng tính năng AI Vision tự động đọc PDF Scan."

    genai.configure(api_key=api_key)
    ext = os.path.splitext(file_name)[1] or ".pdf"
    tmp_path = ""
    media_file = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
            
        media_file = genai.upload_file(path=tmp_path)
        
        # Chờ xử lý file trên server của Google
        while media_file.state.name == "PROCESSING":
            time.sleep(2)
            media_file = genai.get_file(media_file.name)
            
        if media_file.state.name == "FAILED":
            return "❌ Lỗi: AI từ chối đọc file PDF Scan này do lỗi định dạng hoặc giới hạn bảo mật."
            
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        
        ocr_prompt = """Bạn là một chuyên gia nhận diện văn bản (OCR) đẳng cấp thế giới. 
        Hãy đọc và trích xuất toàn bộ nội dung trong tệp đính kèm. 
        YÊU CẦU:
        1. Trích xuất chính xác 100% văn bản.
        2. Các công thức Toán học, Hóa học, Vật lý BẮT BUỘC phải chuyển thành mã LaTeX (ví dụ: dùng $...$ cho inline, $$...$$ cho block).
        3. Vẽ lại các bảng biểu thành dạng Markdown.
        4. Bỏ qua các hình ảnh trang trí không chứa thông tin học thuật."""
        
        response = model.generate_content([ocr_prompt, media_file])
        
        return response.text if response and hasattr(response, "text") else ""
        
    except Exception as e:
        return f"❌ Lỗi khi OCR bằng mắt AI: {str(e)}"
    finally:
        if media_file:
            try:
                genai.delete_file(media_file.name)
            except Exception:
                pass
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    try:
        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
        else:
            if hasattr(uploaded_file, "seek"): uploaded_file.seek(0)
            content = uploaded_file.read()
        if not content: return ""

        range_str = safe_text(range_str)
        selected_start, selected_end = None, None
        if range_str:
            try:
                if "-" in range_str:
                    parts = range_str.split("-", 1)
                    selected_start, selected_end = int(parts[0].strip()), int(parts[1].strip())
                else:
                    selected_start = selected_end = int(range_str)
            except Exception:
                pass

        extracted_text = ""

        # 1. Thử dùng PyMuPDF (Nhanh, nhẹ, cho PDF chuẩn text)
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            total_pages = len(doc)
            if total_pages > 0:
                s_page = 1 if selected_start is None else max(1, selected_start)
                e_page = total_pages if selected_end is None else min(total_pages, selected_end)
                if s_page > e_page: s_page, e_page = 1, total_pages
                
                pages = [doc[i - 1].get_text("text").strip() for i in range(s_page, e_page + 1) if doc[i - 1].get_text("text")]
                extracted_text = "\n\n".join(pages)
        except Exception:
            pass

        # 2. Thử dùng pypdf làm phương án phụ cho text
        if len(extracted_text) < 100:
            try:
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(content))
                total_pages = len(reader.pages)
                if total_pages > 0:
                    s_page = 1 if selected_start is None else max(1, selected_start)
                    e_page = total_pages if selected_end is None else min(total_pages, selected_end)
                    if s_page > e_page: s_page, e_page = 1, total_pages
                    
                    pages = [reader.pages[i - 1].extract_text().strip() for i in range(s_page, e_page + 1) if reader.pages[i - 1].extract_text()]
                    extracted_text = "\n\n".join(pages)
            except Exception as e:
                pass
        
        # 3. KÍCH HOẠT FALLBACK AI VISION (NẾU PHÁT HIỆN LÀ PDF SCAN DẠNG ẢNH)
        if len(extracted_text) < 100:
            try:
                st.toast("⚠️ Phát hiện PDF Scan! Đang kích hoạt luồng AI Vision để tự động đọc ảnh và bảo toàn công thức...", icon="👁️")
                extracted_text = extract_text_via_gemini_ocr(content, getattr(uploaded_file, "name", "document.pdf"))
            except Exception as e:
                logger.error(f"Lỗi Fallback OCR: {e}")

        return safe_text(extracted_text)
    except Exception as e:
        return f"[LỖI ĐỌC PDF: {e}]"


def read_docx_ordered(source):
    try:
        if isinstance(source, (str, Path)): doc = Document(source)
        elif hasattr(source, "getvalue"): doc = Document(BytesIO(source.getvalue()))
        elif hasattr(source, "read"):
            if hasattr(source, "seek"): source.seek(0)
            doc = Document(BytesIO(source.read()))
        else: doc = Document(source)

        result = []
        from docx.text.paragraph import Paragraph
        from docx.table import Table

        for element in doc.element.body:
            if element.tag.endswith("}p"):
                text = safe_text(Paragraph(element, doc).text)
                if text: result.append(text)
            elif element.tag.endswith("}tbl"):
                table = Table(element, doc)
                result.append("\n[BẢNG DỮ LIỆU]")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells if safe_text(cell.text)]
                    if cells: result.append(" | ".join(cells))
        return safe_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC DOCX: {e}]"

def read_uploaded_file(uploaded_file, range_str="", is_pdf_target=False):
    if not uploaded_file: return ""
    ext = Path(getattr(uploaded_file, "name", "").lower()).suffix
    if ext == ".pdf": return read_pdf(uploaded_file, range_str if is_pdf_target else "")
    if ext == ".docx": return read_docx_ordered(uploaded_file)
    return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        content = read_uploaded_file(f, range_str, is_pdf_target)
        if len(content.strip()) > 30:
            result.append(f"\n--- TÀI LIỆU: {getattr(f, 'name', 'Tài liệu')} ---\n{content}")
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    if client is None: raise RuntimeError("Chưa truyền đối tượng Client AI.")
    try:
        if hasattr(client, "generate_text"):
            return client.generate_text(prompt, model_name=model_name, max_tokens=8192)
        
        model_mapping = {
            "3.1 Flash-Lite": "gemini-2.5-flash-lite",
            "3.5 Flash": "gemini-2.5-flash",
            "3.1 Pro": "gemini-2.5-pro",
            "Tư duy mở rộng": "gemini-2.5-pro"
        }
        api_model = model_mapping.get(model_name, "gemini-2.5-flash")
        response = client.models.generate_content(model=api_model, contents=prompt)
        return getattr(response, "text", "").strip()
    except Exception as e:
        logger.error("Lỗi gọi AI: %s", e)
        raise RuntimeError(f"Lỗi kết nối AI: {e}")

def validate_khbd_result(text):
    text = safe_text(text).upper()
    if len(text) < 500: return False, "Nội dung giáo án quá ngắn, vui lòng thử mô hình khác hoặc kiểm tra lại file SGK."
    valid_count = sum(1 for kw in ["MỤC TIÊU", "THIẾT BỊ", "TIẾN TRÌNH", "HOẠT ĐỘNG"] if kw in text)
    if valid_count < 3: return False, "Thiếu các mục cấu trúc bắt buộc của Phụ lục 4 (Mục tiêu, Tiến trình...)."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:15000]
    
    if mode == "tu_dong":
        quality = diagnose_source_quality(source, "Tài liệu SGK")
        # Không chặn ngang bằng Error mà chỉ dùng làm cảnh báo trong prompt nếu cần, 
        # vì OCR Vision có thể trả về thông báo lỗi dạng string, vẫn pass được hàm này.
        if quality["status"] == "empty":
            raise ValueError("File PDF tải lên bị rỗng hoặc Hệ thống AI không thể nhận diện được chữ/ảnh từ file này.")

    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    
    hoa_nhap_block = f"BẮT BUỘC: Đề xuất phương pháp/công cụ hỗ trợ riêng cho nhóm học sinh khuyết tật có đặc điểm sau: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else "Không yêu cầu giáo dục hòa nhập đặc biệt."
    ai_block = "BẮT BUỘC: Thiết kế ít nhất một hoạt động có ứng dụng Trí tuệ Nhân tạo (AI) cho GV hoặc HS." if tich_hop_ai else "Không bắt buộc dùng AI."

    if mode == "chinh_sua":
        nhiem_vu = f"""
        NHIỆM VỤ CỦA BẠN: CHỈNH SỬA VÀ NÂNG CẤP KẾ HOẠCH BÀI DẠY (GIÁO ÁN) GỐC.
        1. Giữ nguyên ưu điểm của giáo án cũ, sửa các lỗi về kiến thức/sư phạm (nếu có).
        2. Bổ sung làm phong phú các Hoạt động Khởi động, Khám phá, Luyện tập, Vận dụng sao cho không bị nhàm chán.
        3. Tích hợp hữu cơ các yêu cầu chuyên biệt sau vào tiến trình:
           - Yêu cầu Năng lực số: {nls_str}
           - {ai_block}
           - {hoa_nhap_block}
        4. Trình bày chuẩn hóa lại toàn bộ theo cấu trúc Phụ lục 4 Công văn 5512/BGDĐT.
        """
    else:
        nhiem_vu = f"""
        NHIỆM VỤ CỦA BẠN: SOẠN MỚI HOÀN TOÀN KẾ HOẠCH BÀI DẠY (GIÁO ÁN) DỰA TRÊN SGK.
        1. Đọc thật kỹ NGUỒN KIẾN THỨC CỐT LÕI (SGK) để rút ra khái niệm, công thức, bảng biểu, bài tập. Tuyệt đối KHÔNG BỊA ĐẶT kiến thức ngoài SGK.
        2. Bài học này kéo dài {so_tiet} tiết. BẮT BUỘC phải phân bổ thời lượng, nội dung và ghi rõ (Ví dụ: ### TIẾT 1: Hoạt động 1, 2. ### TIẾT 2: Hoạt động 3, 4).
        3. Chi tiết hóa từng Hoạt động gồm 4 bước: a) Mục tiêu; b) Nội dung; c) Sản phẩm; d) Tổ chức thực hiện (Rõ GV làm gì, HS làm gì). 
           Đặc biệt ở phần "Nội dung" và "Sản phẩm", hãy tái hiện lại công thức, số liệu thực tế từ SGK vào thay vì chỉ ghi chung chung "Giáo viên yêu cầu học sinh đọc sách".
        4. Tích hợp sâu sắc các yêu cầu sau vào thiết kế:
           - Yêu cầu Năng lực số: {nls_str}
           - {ai_block}
           - {hoa_nhap_block}
        5. Cấu trúc tuân thủ nghiêm ngặt Phụ lục 4 Công văn 5512/BGDĐT.
        """

    return (
        f"BẠN LÀ CHUYÊN GIA SƯ PHẠM VÀ PHƯƠNG PHÁP DẠY HỌC THẾ KỶ 21.\n\n"
        f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n"
        f"--- NHIỆM VỤ CỐT LÕI ---\n{nhiem_vu}\n\n"
        f"--- NGUỒN KIẾN THỨC CỐT LÕI (SGK) ---\n{source}\n\n"
        f"{ga_block}\n"
        f"--- RÀNG BUỘC KỸ THUẬT XUẤT BẢN ---\n"
        f"1. Xuất file bằng định dạng Markdown siêu chuẩn.\n"
        f"2. Công thức Toán học, Vật lí, Hóa học BẮT BUỘC dùng cú pháp LaTeX: dùng dấu $ cho inline (ví dụ: $x^2 + y^2 = r^2$) và $$ cho công thức đứng độc lập (block).\n"
        f"3. Dùng Markdown Table (dấu |) để vẽ các bảng biểu so sánh, phiếu học tập nếu SGK có đề cập.\n"
        f"4. Bắt đầu ngay kết quả bằng # TÊN BÀI HỌC (Không cần dạ vâng hay giải thích).\n"
    )
