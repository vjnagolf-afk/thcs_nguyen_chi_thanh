# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (FULL 100% NĂNG LỰC SỐ TT18 & TEMPLATE)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import base64
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
# KHÔI PHỤC ĐẦY ĐỦ TRỌN VẸN FULL TỪ ĐIỂN KHUNG NĂNG LỰC SỐ (THÔNG TƯ 18)
# ============================================================
KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS). Sử dụng được các công cụ hỗ trợ dạy học trực tuyến để triển khai các phiên học trực tuyến, cung cấp tài liệu học tập và tổ chức các hoạt động dạy học đơn giản.",
            "Thành thạo": "Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ. Thiết kế và triển khai được các hoạt động dạy học theo mô hình kết hợp (blended learning) hiệu quả. Lựa chọn và áp dụng được các công cụ và tài nguyên số phù hợp với mục tiêu dạy học. Hướng dẫn và triển khai được phương pháp dạy học theo dự án trực tuyến, lớp học đảo ngược trên nền tảng quản lí học tập LMS.",
            "Nâng cao": "Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số. Hướng dẫn được đồng nghiệp trong việc thiết kế các trải nghiệm học tập số hóa tiên tiến."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Sử dụng được các kênh giao tiếp số (email, diễn đàn) để trả lời câu hỏi và hỗ trợ người học khi cần thiết.",
            "Thành thạo": "Sử dụng được các kênh giao tiếp số (diễn đàn, LMS, nhóm chat...) để tương tác, giải đáp thắc mắc, cung cấp tài liệu hỗ trợ người học. Sử dụng được dữ liệu học tập số để xác định người học cần hỗ trợ và lựa chọn biện pháp can thiệp phù hợp. Thiết lập được các hoạt động, môi trường số cho phép tương tác, hỗ trợ cá nhân hóa và kịp thời cho người học.",
            "Nâng cao": "Hướng dẫn được đồng nghiệp xây dựng văn hóa hỗ trợ học tập tích cực trên nền tảng số. Sáng tạo, thử nghiệm, phát triển được các công cụ/phương pháp hỗ trợ dạy học thông minh trên nền tảng số."
        },
        "1.3. Cá nhân hóa người học": {
            "Cơ bản": "Xác định được các nhu cầu, sự khác biệt của người học trong sử dụng công nghệ số. Lựa chọn, điều chỉnh được các công cụ và nội dung số phù hợp với nhu cầu của người học.",
            "Thành thạo": "Sử dụng được công nghệ số để thiết kế lộ trình học tập linh hoạt, cho phép người học tự chủ về tốc độ, nội dung và cách thức học tập dựa trên nền tảng số. Thiết kế được các nhiệm vụ học tập phân hóa theo trình độ, năng lực và sở thích của người học trong môi trường trực tuyến. Tích hợp đa dạng, linh hoạt các công cụ số hỗ trợ hoạt động học tập thích ứng, điều chỉnh theo kết quả học tập của người học.",
            "Nâng cao": "Thiết kế được môi trường học tập số cá nhân hóa, cung cấp công cụ cập nhật cho người học tự định hướng, tự điều chỉnh quá trình học tập. Đánh giá được hiệu quả của các chiến lược dạy học cá nhân hóa bằng công nghệ."
        },
        "1.4. Học tập cộng tác": {
            "Cơ bản": "Sử dụng được công cụ số cơ bản để tổ chức cho người học làm việc nhóm đơn giản. Thiết kế được các nhiệm vụ học tập, chia sẻ tài liệu, ý tưởng trên nền tảng số.",
            "Thành thạo": "Thiết kế được các nhiệm vụ học tập yêu cầu người học sử dụng đa dạng công cụ số để cùng xây dựng nội dung, kiến thức. Hướng dẫn được người học kĩ năng giao tiếp, hợp tác hiệu quả trong môi trường số. Sử dụng được công nghệ để quản lý và đánh giá hiệu quả làm việc nhóm, đánh giá quá trình và sản phẩm cộng tác của nhóm.",
            "Nâng cao": "Xây dựng được các dự án cộng tác phức tạp, kết nối người học theo mô hình học tập cộng tác trên nền tảng số. Xây dựng và quản lí được các cộng đồng học tập trực tuyến. Hướng dẫn được đồng nghiệp triển khai học tập cộng tác dựa trên công nghệ số trong nhà trường."
        }
    },
    "2. KIỂM TRA, ĐÁNH GIÁ": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng được hình thức kiểm tra, đánh giá truyền thống, có thể nhập điểm vào hệ thống số. Áp dụng được một số công cụ tạo bài kiểm tra online đơn giản trong hoạt động dạy học.",
            "Thành thạo": "Sử dụng được các công cụ số phổ biến để tạo bài kiểm tra, khảo sát nhằm đánh giá quá trình và đánh giá tổng kết. Kết hợp được một số hình thức đánh giá số đơn giản vào quá trình dạy học. Thiết kế và áp dụng được các hình thức đa dạng, công cụ đánh giá số phù hợp với mục tiêu và nội dung học tập.",
            "Nâng cao": "Sáng tạo triển khai các phương pháp, mô hình đánh giá số tiên tiến, đáp ứng yêu cầu đánh giá năng lực phức hợp. Hướng dẫn được đồng nghiệp xây dựng và áp dụng các chiến lược đánh giá số hiệu quả, công bằng trong nhà trường."
        },
        "2.2. Phân tích kết quả học tập": {
            "Cơ bản": "Sử dụng được các chức năng cơ bản của LMS/công cụ đánh giá để xem báo cáo về hoạt động, kết quả của người học.",
            "Thành thạo": "Phân tích được dữ liệu từ các hệ thống đánh giá số để nhận diện quá trình tiến bộ và thành tích học tập của người học. Sử dụng được dữ liệu, công cụ trực quan hóa dữ liệu để xây dựng báo cáo đánh giá sự tiến bộ của người học. Xây dựng được các bảng điều khiển tự động (dashboard) dữ liệu học tập trực quan.",
            "Nâng cao": "Áp dụng được các kĩ thuật phân tích dữ liệu học tập nâng cao để dự đoán xu hướng, phát hiện sớm các vấn đề và đề xuất can thiệp. Hướng dẫn được đồng nghiệp về cách khai thác và diễn giải dữ liệu để cải tiến dạy học."
        },
        "2.3. Phản hồi và đánh giá cải tiến": {
            "Cơ bản": "Sử dụng được các chức năng cung cấp phản hồi trên hệ thống LMS. Cung cấp phản hồi kịp thời cho người học bằng văn bản hoặc điểm số thông qua các nền tảng số.",
            "Thành thạo": "Sử dụng được đa dạng công cụ số (ghi âm, video ngắn, bình luận trực tiếp trên tài liệu) để đưa ra phản hồi chi tiết, kịp thời. Thiết kế được các qui trình phản hồi và đánh giá cải tiến có sự tham gia của người học (tự đánh giá, đánh giá chéo) bằng công nghệ.",
            "Nâng cao": "Sử dụng được dữ liệu phân tích để điều chỉnh kế hoạch bài dạy, phương pháp và cung cấp nhiệm vụ học tập hỗ trợ cá nhân người học. Hướng dẫn được đồng nghiệp sử dụng phản hồi bằng công cụ số và dữ liệu học tập để cải tiến liên tục chương trình và hoạt động giáo dục."
        }
    },
    "3. TRAO QUYỀN CHO NGƯỜI HỌC": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "Sử dụng được các công cụ số cơ bản để hỗ trợ người học gặp khó khăn trong học tập. Lựa chọn và sử dụng được các công cụ, tài nguyên số có tính đến sự đa dạng của người học (đa dạng ngôn ngữ, phong cách học, người học khuyết tật). Đảm bảo mọi người học có cơ hội sử dụng thiết bị, hạ tầng số của nhà trường khi cần thiết.",
            "Thành thạo": "Khai thác, lựa chọn và điều chỉnh được tài nguyên, đa dạng hóa công cụ số để đáp ứng nhu cầu đặc biệt của người học. Thiết kế được nội dung, tài nguyên số đảm bảo tính tiếp cận và hòa nhập trong môi trường số.",
            "Nâng cao": "Hướng dẫn được đồng nghiệp về chiến lược và công nghệ số hỗ trợ giáo dục hòa nhập."
        },
        "3.2. Giải quyết vấn đề": {
            "Cơ bản": "Thiết kế được các nhiệm vụ học tập yêu cầu người học sử dụng Internet để tìm kiếm thông tin để trả lời câu hỏi hoặc giải quyết vấn đề học tập đơn giản.",
            "Thành thạo": "Thiết kế được các nhiệm vụ dự án học tập yêu cầu người học sử dụng công nghệ số để xác định vấn đề, thu thập, phân tích thông tin và đề xuất giải pháp. Tổ chức được các hoạt động học tập dựa trên vấn đề (problem-based) hoặc dự án (project-based) phức tạp, trong đó công nghệ số là công cụ thiết yếu để nghiên cứu, hợp tác và tạo ra sản phẩm.",
            "Nâng cao": "Hướng dẫn được đồng nghiệp xây dựng hệ sinh thái học tập số, kết nối người học với các chuyên gia và vấn đề thực tiễn bên ngoài nhà trường để giải quyết các vấn đề thực tế của cộng đồng."
        },
        "3.3. Khuyến khích sự tham gia tích cực của người học": {
            "Cơ bản": "Sáng tạo và điều phối tương tác số đơn giản để thu hút sự chú ý và khuyến khích người học tham gia vào hoạt động học tập. Tích hợp được công nghệ số trong dạy học nhằm trực quan hóa và tăng hiệu quả trình bày nội dung dạy học.",
            "Thành thạo": "Tích hợp được các yếu tố trò chơi hóa, tương tác và các công cụ sáng tạo nội dung để thúc đẩy người học chủ động, tích cực tham gia vào bài học. Thiết kế được hoạt động khuyến khích người học tự tạo ra nội dung số, chia sẻ kiến thức thông qua các nền tảng số, giải quyết vấn đề bằng mô phỏng, thí nghiệm ảo, thực tế ảo, thực tế ảo tăng cường.",
            "Nâng cao": "Sử dụng được các công cụ để thiết kế môi trường học tập số năng động, lấy người học làm trung tâm. Hướng dẫn được đồng nghiệp sáng tạo triển khai các hoạt động học tập tích cực bằng công nghệ số."
        }
    },
    "4. KĨ NĂNG CÔNG NGHỆ SỐ": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "Sử dụng được công cụ tìm kiếm để tìm thông tin, tài liệu phục vụ bài giảng. Lưu trữ và sắp xếp một cách khoa học các dữ liệu trên máy tính hoặc đám mây.",
            "Thành thạo": "Đánh giá được độ tin cậy của nguồn tin trên Internet, mạng xã hội. Sử dụng được các kĩ thuật tìm kiếm nâng cao. Hướng dẫn được người học các kĩ năng tư duy phản biện khi tìm kiếm, xử lí, tiếp nhận thông tin số từ các nguồn khác nhau. Tổ chức được các nhiệm vụ học tập nâng cao cho phép người học chủ động tìm kiếm và xử lí thông tin trong môi trường số.",
            "Nâng cao": "Sử dụng được công cụ để thu thập và trực quan hóa dữ liệu đơn giản, phân tích và đánh giá độ tin cậy của thông tin trong quá trình dạy học. Hướng dẫn được đồng nghiệp tích hợp phát triển năng lực thông tin vào chương trình dạy học."
        },
        "4.2. Sáng tạo nội dung số": {
            "Cơ bản": "Sử dụng được các công cụ số phổ biến để tạo nội dung dạy học theo định dạng số khác nhau. Tích hợp được các định dạng số trong nội dung thực hiện nhiệm vụ của người học.",
            "Thành thạo": "Tích hợp được công nghệ số trong hoạt động sáng tạo nội dung số, xây dựng kho học liệu số. Hướng dẫn được người học sử dụng các công cụ cơ bản để tạo nội dung số, thực hiện quyền tác giả, giấy phép, cách trích dẫn, sử dụng và chia sẻ tài nguyên số hợp pháp. Sử dụng được nền tảng, công cụ số đa dạng để tạo và chia sẻ nội dung hợp lệ.",
            "Nâng cao": "Sử dụng thành thạo các công cụ chuyên dụng để tạo ra các học liệu số có tính tương tác cao. Hướng dẫn được đồng nghiệp phát triển nền tảng học tập tích hợp AI, thực tế ảo, thực tế ảo tăng cường trong sáng tạo nội dung số vào các môn học."
        },
        "4.3. An toàn": {
            "Cơ bản": "Có hiểu biết về bảo vệ sức khỏe thể chất, tinh thần, đảm bảo an sinh số trong hoạt động dạy học. Bố trí, sắp xếp được không gian, thời gian sử dụng thiết bị, công cụ số hợp lí cho người học. Nhận diện và xử lí được các tình huống bắt nạt trực tuyến.",
            "Thành thạo": "Tích hợp được kiến thức, kĩ năng nhận diện và phòng tránh các rủi ro phổ biến trên mạng trong quá trình dạy học. Áp dụng được các biện pháp bảo vệ dữ liệu cá nhân và của người học. Thực hiện được các biện pháp cơ bản đảm bảo an toàn thiết bị, tài khoản trong lớp học và hướng dẫn người học cách bảo vệ dữ liệu cá nhân, định danh số, quản lí dấu vết số.",
            "Nâng cao": "Thực hiện được các biện pháp đảm bảo an toàn sức khỏe, áp dụng các phương pháp dạy học giảm căng thăng trong môi trường số cho người học. Cập nhật và phổ biến các xu hướng, mối đe dọa mới và cách phòng chống cho cộng đồng giáo viên, phụ huynh. Hướng dẫn được đồng nghiệp xây dựng môi trường học tập số an toàn, lành mạnh trong lớp học và nhà trường."
        }
    },
    "5. PHÁT TRIỂN CHUYÊN MÔN": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "Sử dụng được email, nhóm chat của trường/tổ để trao đổi thông tin công việc và giao tiếp với phụ huynh.",
            "Thành thạo": "Sử dụng hiệu quả các kênh giao tiếp số chính thức của trường để tương tác với các bên liên quan, phù hợp với từng đối tượng và mục đích giáo dục. Sử dụng được công cụ số cơ bản để giao tiếp, chia sẻ thông tin, dữ liệu và tham gia hoạt động chuyên môn với đồng nghiệp.",
            "Nâng cao": "Xây dựng và quản lí được chiến lược truyền thông số, các kênh truyền thông số chính thức của trường để chia sẻ và kết nối cộng đồng. Hướng dẫn được đồng nghiệp đổi mới cách thức giao tiếp trong tổ chức bằng công nghệ số tăng cường tính minh bạch, sự tham gia của các bên liên quan."
        },
        "5.2. Hợp tác phát triển chuyên môn": {
            "Cơ bản": "Chủ động tham gia các cộng đồng học tập trực tuyến. Tự đánh giá được khó khăn, thách thức và thuận lợi ứng dụng công nghệ số trong công việc.",
            "Thành thạo": "Xây dựng được kế hoạch cải tiến, đổi mới ứng dụng công nghệ số trong hoạt động chuyên môn. Chủ động tìm kiếm và tham gia các khóa học cơ bản để cập nhật kiến thức, kĩ năng số. Tự đánh giá, cải tiến ứng dụng công nghệ số trong dạy học trong môi trường số. Tham gia chia sẻ, học tập và cập nhật kĩ năng ứng dụng công nghệ số với đồng nghiệp.",
            "Nâng cao": "Cập nhật được các xu hướng công nghệ và phương pháp sư phạm số mới, áp dụng kiến thức, kĩ năng số vào thực tiễn dạy học. Hướng dẫn được đồng nghiệp xây dựng các yêu cầu về dạy học trong môi trường số, phát triển các công cụ, phương pháp hỗ trợ tự phản ánh về năng lực số."
        },
        "5.3. Phát triển, sử dụng, chia sẻ và quản lí học liệu số": {
            "Cơ bản": "Sử dụng được các công cụ tìm kiếm phổ biến để tìm kiếm tài nguyên, kho học liệu số, thư viện trực tuyến, tài nguyên giáo dục mở (OER). Lựa chọn được tài nguyên phù hợp với mục tiêu bài học.",
            "Thành thạo": "Lựa chọn và sử dụng được tài nguyên, học liệu số phù hợp với đối tượng đa dạng của người học. Tạo được tài nguyên số phục vụ cho môn học dựa từ các nguồn có sẵn. Tổ chức lưu trữ, quản lí và chia sẻ được kho học liệu số cá nhân một cách khoa học, an toàn. Đánh giá được chất lượng, độ tin cậy, tính pháp lí và sư phạm của tài nguyên, học liệu số.",
            "Nâng cao": "Xây dựng và quản trị được các hệ thống quản lí, chia sẻ tài nguyên số cho tổ/trường. Hướng dẫn được đồng nghiệp xây dựng và quản trị kho học liệu số mở của nhà trường."
        }
    },
    "6. ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Nhận diện được cách vận hành của AI và các công nghệ có tích hợp AI.",
            "Thành thạo": "Thiết kế được các hoạt động dạy học tích hợp AI một cách sáng tạo và có trách nhiệm.",
            "Nâng cao": "Triển khai đổi mới phương pháp dạy học mới có tích hợp sâu AI đáp ứng cá nhân hóa và dạy học thích ứng. Hướng dẫn, lựa chọn và đề xuất sử dụng các công cụ AI phù hợp cho đồng nghiệp."
        },
        "6.2. Đạo đức AI": {
            "Cơ bản": "Nhận diện được các khả năng tích hợp sử dụng AI trong hỗ trợ hoạt động dạy học. Sử dụng được các công cụ AI đơn giản (chủ yếu là AI tạo sinh) để hỗ trợ dạy học và kiểm tra đánh giá. Nhận diện được khả năng thu thập dữ liệu và thông tin cá nhân khi sử dụng công cụ AI, những tiềm ẩn rủi ro khi sử dụng AI không đúng cách. Thể hiện sự cẩn trọng và có trách nhiệm đối với quyền riêng tư của người học, có trách nhiệm khi sử dụng công cụ AI trong dạy học, kiểm tra đánh giá. Thiết kế các hoạt động giáo dục tích hợp AI, cân bằng giữa tương tác công nghệ và tương tác xã hội, phát triển tư duy phản biện.",
            "Thành thạo": "Khai thác hiệu quả các công cụ AI chuyên biệt cho giáo dục để tạo học liệu số tương tác đa dạng, cá nhân hóa một phần nội dung/bài tập, hỗ trợ chấm điểm tự động. Hướng dẫn được người học sử dụng AI có trách nhiệm, nhận biết ưu/nhược điểm và các rủi ro liên quan khi sử dụng AI. Thực hiện được các biện pháp cần thiết phòng ngừa rủi ro và về các vấn đề đạo đức cơ bản khi sử dụng AI. Lựa chọn, đánh giá được các ứng dụng AI dựa trên tiêu chí về đạo đức, chính sách bảo mật, sự công bằng trong tiếp cận và tác động khác trong dạy học, kiểm tra đánh giá. Thiết kế và tích hợp hoạt động hướng dẫn người học sử dụng AI an toàn và có đạo đức trong hoạt động học tập.",
            "Nâng cao": "Đánh giá được ưu/nhược điểm và các vấn đề đạo đức của công cụ AI trong giáo dục, cập nhật, hướng dẫn và chia sẻ với đồng nghiệp các vấn đề về đạo đức sử dụng AI. Tham gia xây dựng chính sách, hướng dẫn về sử dụng AI có đạo đức trong nhà trường."
        },
        "6.3. Sư phạm AI": {
            "Cơ bản": "Nhận diện được khả năng tích hợp AI theo hướng cá nhân hóa và lấy người học làm trung tâm. Có hiểu biết về lợi ích sư phạm của công cụ AI để hỗ trợ dạy học.",
            "Thành thạo": "Ứng dụng được công cụ AI linh hoạt trong các bước dạy học đảm bảo nguyên tắc lấy người học làm trung tâm, giáo dục hòa nhập. Lựa chọn và ứng dụng được các hệ thống, công cụ AI phù hợp, giảm thiểu rủi ro trong thiết kế dạy học, kiểm tra đánh giá. Tổ chức và quản lý được hoạt động tương tác 3 chiều giữa giáo viên, người học với các công cụ AI trong dạy học.",
            "Nâng cao": "Xây dựng được nguyên tắc sư phạm sử dụng AI trong hoạt động dạy học. Hướng dẫn được đồng nghiệp thiết kế và sử dụng AI theo tiếp cận đồng sáng tạo, lấy con người làm trung tâm trong các hoạt động sư phạm."
        },
        "6.4. AI cho phát triển chuyên môn": {
            "Cơ bản": "Nhận diện được sự cân bằng giữa vai trò của người giáo viên và nhiệm vụ phát triển năng lực số, năng lực AI trong dạy học. Sử dụng được công cụ AI phù hợp để lập kế hoạch, theo dõi và phân tích quá trình phát triển chuyên môn của bản thân.",
            "Thành thạo": "Sử dụng được các công cụ AI đơn giản (chủ yếu là AI tạo sinh) để hỗ trợ học tập suốt đời và phát triển chuyên môn nghiệp vụ bản thân. Đề xuất được các hướng sử dụng hiệu quả các nền tảng AI để tìm kiếm tài nguyên, tham gia cộng đồng thực hành hỗ trợ phát triển bản thân. Đánh giá được các rủi ro đạo đức từ các nền tảng AI và triển khai các biện pháp phòng ngừa giảm thiểu tác động tiêu cực.",
            "Nâng cao": "Hướng dẫn đổi mới sáng tạo cho đồng nghiệp dựa trên các nền tảng AI phù hợp và tiếp cận sư phạm số. Xây dựng hoặc sử dụng được các bộ công cụ AI tạo sinh hỗ trợ phát triển chuyên môn của đồng nghiệp."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {"Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản.", "Mức 2": "Biết đánh giá độ tin cậy của thông tin."}
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {"Mức 1": "Biết sử dụng email, chat để trao đổi học tập.", "Mức 2": "Biết sử dụng nền tảng làm việc nhóm (Padlet, Azota...)."}
    }
}

def get_nls_framework(loai_khung): return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS
def get_nls_domains(loai_khung): return list(get_nls_framework(loai_khung).keys())
def get_nls_components(loai_khung, linh_vuc): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())
def get_nls_levels(loai_khung, linh_vuc, thanh_phan): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())
def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do): return get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).get(muc_do, "")

def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return
    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "Khung DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list: st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.get("khbd_nls_list", [])
    if not items:
        return "- Năng lực 1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ > 1.1. Dạy học và giáo dục trong môi trường số (Thành thạo): Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ, lựa chọn và áp dụng các công cụ số phù hợp với mục tiêu dạy học."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    return re.sub(r"[ ]{2,}", " ", text).strip()

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    if len(text) < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} quá ngắn hoặc không đọc được chữ."}
    return {"status": "valid", "message": "Dữ liệu hợp lệ."}

def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    extracted_text = ""
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = "\n\n".join([doc[i].get_text("text").strip() for i in range(len(doc))])
    except: pass
    return safe_text(extracted_text)

def read_docx_ordered(source):
    try:
        doc = Document(BytesIO(source.getvalue())) if hasattr(source, "getvalue") else Document(source)
        return safe_text("\n".join([p.text for p in doc.paragraphs]))
    except: return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        file_name = getattr(f, 'name', '').lower()
        if file_name.endswith('.pdf'): content = read_pdf(f)
        else: content = read_docx_ordered(f)
        if len(content) > 30: result.append(content)
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    system_instruction = """
[KỶ LUẬT THÉP VỀ NỘI DUNG VÀ CẤU TRÚC TEMPLATE - ĐỌC KỸ VÀ TUÂN THỦ 100%]:
1. CẤM VIẾT LỜI CHÀO/KẾT LUẬN. Bắt đầu ngay lập tức bằng "# TÊN BÀI HỌC:".
2. BẠN PHẢI TUÂN THỦ TUYỆT ĐỐI CẤU TRÚC TEMPLATE SAU:
   I. MỤC TIÊU
   1. Kiến thức
   2. Năng lực
      a) Năng lực chung:
      b) Năng lực đặc thù:
   3. Năng lực số và AI (Ghi đầy đủ chi tiết các năng lực số từ Thông tư 18/2026/TT-BGDĐT)
   4. Phẩm chất
   II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
   1. Giáo viên:
   2. Học sinh:
   III. TIẾN TRÌNH DẠY HỌC
   (Chia các HOẠT ĐỘNG: MỞ ĐẦU, HÌNH THÀNH KIẾN THỨC MỚI, LUYỆN TẬP, VẬN DỤNG)
   PHỤ LỤC
   PHIẾU HỌC TẬP
3. QUY TẮC CỨNG Ở PHẦN "d) Tổ chức thực hiện": BẮT BUỘC dùng chính xác 4 gạch đầu dòng bắt đầu bằng dấu * và mỗi ý PHẢI NẰM TRÊN MỘT DÒNG RIÊNG BIỆT:
   *Chuyển giao nhiệm vụ học tập: ...
   *Thực hiện nhiệm vụ học tập: ...
   *Báo cáo kết quả và thảo luận: ...
   *Kết luận: ...
4. TOÁN HỌC: Dùng chuẩn LaTeX `$\sqrt{x}$`.
    """
    full_prompt = system_instruction + "\n\n" + prompt

    api_key = st.session_state.get("user_api_key", "").strip()
    if not api_key:
        try: api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        except: pass
    if not api_key:
        try: api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
        except: pass

    text_out = ""
    try:
        if api_key.startswith("sk-") or "proj-" in api_key:
            import openai
            oai_client = openai.OpenAI(api_key=api_key)
            gpt_model = "gpt-4o" if "Pro" in model_name else "gpt-4o-mini"
            response = oai_client.chat.completions.create(
                model=gpt_model,
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],
                max_tokens=8192
            )
            text_out = response.choices[0].message.content.strip()
        else:
            import google.generativeai as genai
            genai.configure(api_key=api_key or "AIzaSy_dummy")
            api_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name=api_model)
            response = model.generate_content(full_prompt)
            text_out = getattr(response, "text", "").strip()
    except Exception as e:
        logger.error(f"AI Generation Error: {e}")
        raise RuntimeError(f"Lỗi kết nối AI: {e}")

    if not text_out:
        raise RuntimeError("Không thể nhận phản hồi từ AI.")

    if "# TÊN BÀI HỌC:" in text_out:
        text_out = text_out[text_out.find("# TÊN BÀI HỌC:"):]
        
    text_out = re.sub(r'(?<!\n)\s*([a-d]\))', r'\n\1', text_out)
    text_out = re.sub(r'([^\n])\s*(\*(?:Chuyển giao|Thực hiện|Báo cáo|Kết luận|Đánh giá)[^:\n]*:)', r'\1\n\n\2', text_out)
    
    return text_out

def validate_khbd_result(text):
    if len(text) < 500: return False, "Nội dung quá ngắn."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:20000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    hoa_nhap_block = f"- Dạy học hòa nhập: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = f"- Tích hợp AI: Đề xuất hoạt động." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY SIÊU CHI TIẾT TỪ NGUỒN CUNG CẤP.
1. TRÍCH XUẤT NGUYÊN VĂN BÀI TẬP VÀ GIẢI CHI TIẾT (DÙNG LATEX $...$).
2. Bài học kéo dài {so_tiet} tiết. Phân bổ kiến thức đều đặn.
3. DÀN Ý BẮT BUỘC:
# TÊN BÀI HỌC: ...
I. MỤC TIÊU
1. Kiến thức
2. Năng lực
   a) Năng lực chung:
   b) Năng lực đặc thù:
3. Năng lực số và AI
   [Nội dung chuẩn Thông tư 18/2026/TT-BGDĐT]: {nls_str} 
   {ai_block} 
   {hoa_nhap_block}
4. Phẩm chất
II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
1. Giáo viên:
2. Học sinh:
III. TIẾN TRÌNH DẠY HỌC
### TIẾT 1
**Hoạt động 1: MỞ ĐẦU**
a) Mục tiêu: ...
b) Nội dung: ...
c) Sản phẩm: ...
d) Tổ chức thực hiện: 
*Chuyển giao nhiệm vụ học tập: ...
*Thực hiện nhiệm vụ học tập: ...
*Báo cáo kết quả và thảo luận: ...
*Kết luận: ...

PHỤ LỤC
PHIẾU HỌC TẬP
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC ---\n{source}\n\n{ga_block}"
