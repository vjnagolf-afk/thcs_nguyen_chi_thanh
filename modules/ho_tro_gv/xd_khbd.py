prompt = f"""
            Đóng vai là một giáo viên {mon_hoc} cấp THCS xuất sắc.
            Hãy soạn Kế hoạch bài dạy cho bài: "{ten_bai}", Lớp {lop}, thời lượng {thoi_luong} tiết.
            Yêu cầu chuyên môn bổ sung: {yeu_cau_them}

            NHIỆM VỤ QUAN TRỌNG NHẤT:
            Bạn BẮT BUỘC phải trả về kết quả dưới định dạng JSON nguyên chuẩn (không có markdown, không có chữ text nào ngoài JSON). 
            Các Key trong JSON phải khớp chính xác 100% với cấu trúc dưới đây để tôi đổ vào file Word:
            {{
                "CHU_DE": "Tên chủ đề",
                "TEN_BAI_HOC": "{ten_bai}",
                "MON_HOC": "{mon_hoc}",
                "THOI_LUONG": "{thoi_luong}",
                "MUC_TIEU_KIEN_THUC": "Nội dung chi tiết mục tiêu kiến thức",
                "NANG_LUC_CHUNG": "Tự chủ tự học, giao tiếp, hợp tác...",
                "NANG_LUC_DAK_THU": "Năng lực đặc thù của môn học",
                "NANG_LUC_SO_VA_AI": "Ứng dụng công cụ số hoặc nhận thức cơ bản về AI trong bài học",
                "PHAM_CHAT": "Trung thực, trách nhiệm...",
                "GIAO_VIEN": "Máy chiếu, phiếu học tập, AI chatbot...",
                "HOC_SINH": "Sách vở, dụng cụ...",
                
                "HOAT_DONG_MO_DAU": "Tên hoạt động khởi động",
                "MUC_TIEU": "Mục tiêu HĐ 1",
                "NOI_DUNG": "Nội dung trò chơi/tình huống HĐ 1",
                "SAN_PHAM": "Câu trả lời dự kiến HĐ 1",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Cách GV giao nhiệm vụ HĐ 1",
                "THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ 1",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo kết quả HĐ 1",
                "DANH_GIA_KET_QUA": "GV đánh giá HĐ 1",

                "TEN_HOAT_DONG": "Tên hoạt động khám phá 2.1",
                "HD1_MUC_TIEU": "Mục tiêu HĐ 2.1",
                "HD1_NOI_DUNG": "Nội dung HĐ 2.1",
                "HD1_SAN_PHAM": "Sản phẩm HĐ 2.1",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1": "Cách giao nhiệm vụ HĐ 2.1",
                "THUC_HIEN_NHIEM_VU_HOC_TAP_1": "HS thực hiện HĐ 2.1",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN_1": "Báo cáo HĐ 2.1",
                "KET_LUAN_1": "Chốt kiến thức HĐ 2.1",

                "HD2_MUC_TIEU": "Mục tiêu HĐ 2.2",
                "HD2_NOI_DUNG": "Nội dung HĐ 2.2",
                "HD2_SAN_PHAM": "Sản phẩm HĐ 2.2",
                "HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Cách giao nhiệm vụ HĐ 2.2",
                "HD2_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ 2.2",
                "HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ 2.2",
                "HD2_KET_LUAN": "Chốt kiến thức HĐ 2.2",

                "LT_MUC_TIEU": "Mục tiêu HĐ Luyện tập",
                "LT_NOI_DUNG": "Nội dung HĐ Luyện tập",
                "LT_SAN_PHAM": "Sản phẩm HĐ Luyện tập",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT": "Cách giao nhiệm vụ HĐ Luyện tập",
                "LT_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ Luyện tập",
                "LT_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Luyện tập",
                "LT_KET_LUAN": "Chốt kỹ năng HĐ Luyện tập",

                "VD_MUC_TIEU": "Mục tiêu HĐ Vận dụng",
                "VD_NOI_DUNG": "Nhiệm vụ thực tế HĐ Vận dụng",
                "VD_SAN_PHAM": "Sản phẩm thực hành HĐ Vận dụng",
                "TO_CHUC_THUC_HIEN": "Cách tổ chức thực hiện HĐ Vận dụng",
                "VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Giao việc về nhà",
                "VD_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ Vận dụng",
                "VD_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Vận dụng",
                "VD_KET_LUAN": "Đánh giá chung HĐ Vận dụng",

                "TIET_2": "Hướng dẫn hoặc nội dung chuyển tiếp sang Tiết 2",
                "PHU_LUC": "Ghi chú phụ lục",
                "PHIEU_HOC_TAP": "Nội dung chi tiết các câu hỏi trong Phiếu học tập"
            }}
            """
