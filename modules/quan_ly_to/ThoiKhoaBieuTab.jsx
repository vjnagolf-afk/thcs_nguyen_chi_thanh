import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import * as XLSX from 'xlsx';
import { Upload, Trash2, Calendar, User, BookOpen, Layers } from 'lucide-react';

// Khởi tạo Supabase client (Thay thế bằng URL và Anon Key của thầy)
const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
const supabase = createClient(supabaseUrl, supabaseKey);

export default function ThoiKhoaBieuTab() {
  const [batches, setBatches] = useState([]);
  const [selectedBatchId, setSelectedBatchId] = useState('');
  const [batchNameInput, setBatchNameInput] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chung'); // 'chung' hoặc 'giaovien'
  
  // Dữ liệu hiển thị
  const [tkbChung, setTkbChung] = useState([]);
  const [danhSachGiaoVien, setDanhSachGiaoVien] = useState([]);
  const [selectedTeacher, setSelectedTeacher] = useState('');
  const [tkbGiaoVien, setTkbGiaoVien] = useState([]);

  useEffect(() => {
    fetchBatches();
  }, []);

  useEffect(() => {
    if (selectedBatchId) {
      fetchTkbData(selectedBatchId);
    } else {
      setTkbChung([]);
      setDanhSachGiaoVien([]);
    }
  }, [selectedBatchId]);

  // Lấy danh sách các đợt TKB
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !batchNameInput.trim()) {
      alert('Vui lòng nhập tên đợt và chọn file Excel!');
      return;
    }

    setLoading(true);
    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const json = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

      // Tạo đợt TKB mới trong bảng tkb_batches
      const { data: batchData, error: batchError } = await supabase
        .from('tkb_batches')
        .insert([{ batch_name: batchNameInput }])
        .select()
        .single();

      if (batchError) throw batchError;
      const batchId = batchData.id;

      // Phân tích dữ liệu từ hàng thứ 5 (index 4 là tiêu đề lớp, từ index 5 trở xuống là tiết)
      // Cột 0: Thứ, Cột 1: Tiết
      // Từ Cột 2 trở đi là các lớp học
      const headers = json[4] || [];
      const rowsToInsert = [];

      let currentThu = '';
      for (let i = 5; i < json.length; i++) {
        const row = json[i];
        if (!row || row.length === 0) continue;

        if (row[0]) currentThu = row[0]; // Cập nhật thứ nếu có
        const tiet = row[1];

        if (!tiet) continue;

        for (let colIndex = 2; colIndex < headers.length; colIndex++) {
          const rawHeader = headers[colIndex];
          if (!rawHeader) continue;
          
          // Lấy tên lớp (phần trước dấu xuống dòng hoặc toàn bộ header)
          const lop = String(rawHeader).split('\n')[0].trim();
          const cellValue = row[colIndex];

          if (cellValue) {
            // Xử lý bóc tách Môn học và Giáo viên theo yêu cầu:
            // "Tên của GV là những kí tự đúng sau dấu gạch ngang cuối cùng."
            const cellStr = String(cellValue).trim();
            const lastDashIndex = cellStr.lastIndexOf('-');
            
            let monHoc = cellStr;
            let giaoVien = 'Chưa phân công';

            if (lastDashIndex !== -1) {
              monHoc = cellStr.substring(0, lastDashIndex).trim();
              giaoVien = cellStr.substring(lastDashIndex + 1).trim();
            }

            rowsToInsert.push({
              batch_id: batchId,
              thu: String(currentThu || 'Sáng'),
              tiet: String(tiet),
              lop: lop,
              mon_hoc: monHoc,
              giao_vien: giaoVien
            });
          }
        }
      }

      // Lưu vào Supabase theo từng batch (chia nhỏ nếu quá nhiều)
      if (rowsToInsert.length > 0) {
        const chunkSize = 500;
        for (let i = 0; i < rowsToInsert.length; i += chunkSize) {
          const chunk = rowsToInsert.slice(i, i + chunkSize);
          const { error: insertError } = await supabase.from('tkb_details').insert(chunk);
          if (insertError) throw insertError;
        }
      }

      alert('Tải lên và xử lý Thời khóa biểu thành công!');
      setBatchNameInput('');
      setFile(null);
      fetchBatches();
      setSelectedBatchId(batchId);
    } catch (error) {
      console.error(error);
      alert('Đã xảy ra lỗi khi xử lý file: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchBatches = async () => {
    const { data, error } = await supabase.from('tkb_batches').select('*').order('created_at', { ascending: false });
    if (!error && data) {
      setBatches(data);
      if (data.length > 0 && !selectedBatchId) {
        setSelectedBatchId(data[0].id);
      }
    }
  };

  const fetchTkbData = async (batchId) => {
    const { data, error } = await supabase.from('tkb_details').select('*').eq('batch_id', batchId);
    if (!error && data) {
      setTkbChung(data);
      // Lấy danh sách giáo viên duy nhất
      const gvSet = [...new Set(data.map(item => item.giao_vien))].filter(Boolean).sort();
      setDanhSachGiaoVien(gvSet);
      if (gvSet.length > 0) {
        setSelectedTeacher(gvSet[0]);
      }
    }
  };

  // Lọc TKB theo giáo viên được chọn
  useEffect(() => {
    if (selectedTeacher && tkbChung.length > 0) {
      const filtered = tkbChung.filter(item => item.giao_vien === selectedTeacher);
      setTkbGiaoVien(filtered);
    } else {
      setTkbGiaoVien([]);
    }
  }, [selectedTeacher, tkbChung]);

  const handleDeleteBatch = async () => {
    if (!selectedBatchId) return;
    if (!window.confirm('Thầy có chắc chắn muốn xóa đợt Thời khóa biểu này không?')) return;

    const { error } = await supabase.from('tkb_batches').delete().eq('id', selectedBatchId);
    if (!error) {
      alert('Đã xóa thành công!');
      setSelectedBatchId('');
      fetchBatches();
    } else {
      alert('Lỗi khi xóa: ' + error.message);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-7xl mx-auto">
      <h2 className="text-2xl font-bold text-red-700 mb-6 flex items-center gap-2">
        <Calendar className="w-7 h-7" /> Quản lý Thời Khóa Biểu Toàn Trường
      </h2>

      {/* Phần tải lên và chọn đợt */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-gray-50 p-4 rounded-lg mb-6 border">
        <form onSubmit={handleUpload} className="space-y-4">
          <h3 className="font-semibold text-gray-700 flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-600" /> Tải lên TKB mới (Excel)
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Tên đợt TKB:</label>
            <input
              type="text"
              value={batchNameInput}
              onChange={(e) => setBatchNameInput(e.target.value)}
              placeholder="Ví dụ: TKB số 7 - Học kỳ 2 (2025-2026)"
              className="w-full p-2 border rounded-md focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Chọn file Excel (.xlsx):</label>
            <input
              type="file"
              accept=".xlsx, .xls"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full p-1 border rounded-md bg-white"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 font-medium transition flex items-center gap-2"
          >
            {loading ? 'Đang xử lý và lưu lên Supabase...' : 'Tải lên & Lưu TKB'}
          </button>
        </form>

        <div className="space-y-4 border-t md:border-t-0 md:border-l md:pl-6 pt-4 md:pt-0">
          <h3 className="font-semibold text-gray-700 flex items-center gap-2">
            <Layers className="w-5 h-5 text-green-600" /> Chọn đợt TKB để xem
          </h3>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Danh sách các đợt đã lưu:</label>
            <select
              value={selectedBatchId}
              onChange={(e) => setSelectedBatchId(e.target.value)}
              className="w-full p-2 border rounded-md bg-white"
            >
              <option value="">-- Chọn đợt TKB --</option>
              {batches.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.batch_name} ({new Date(b.created_at).toLocaleDateString('vi-VN')})
                </option>
              ))}
            </select>
          </div>
          {selectedBatchId && (
            <button
              onClick={handleDeleteBatch}
              className="bg-red-100 text-red-700 border border-red-300 px-4 py-2 rounded-md hover:bg-red-200 font-medium transition flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" /> Xóa đợt TKB đang chọn
            </button>
          )}
        </div>
      </div>

      {/* Chuyển đổi tab xem */}
      {selectedBatchId && (
        <div>
          <div className="flex border-b mb-4">
            <button
              onClick={() => setActiveTab('chung')}
              className={`py-2 px-4 font-medium border-b-2 flex items-center gap-2 ${
                activeTab === 'chung' ? 'border-red-600 text-red-600' : 'border-transparent text-gray-500'
              }`}
            >
              <BookOpen className="w-4 h-4" /> TKB Chung Cả Trường ({tkbChung.length} tiết)
            </button>
            <button
              onClick={() => setActiveTab('giaovien')}
              className={`py-2 px-4 font-medium border-b-2 flex items-center gap-2 ${
                activeTab === 'giaovien' ? 'border-red-600 text-red-600' : 'border-transparent text-gray-500'
              }`}
            >
              <User className="w-4 h-4" /> Xem TKB Theo Giáo Viên
            </button>
          </div>

          {/* Nội dung Tab TKB Chung */}
          {activeTab === 'chung' && (
            <div className="overflow-x-auto border rounded-lg max-h-[600px]">
              <table className="w-full text-left border-collapse text-sm">
                <thead className="bg-gray-100 sticky top-0">
                  <tr>
                    <th className="p-3 border">Thứ</th>
                    <th className="p-3 border">Tiết</th>
                    <th className="p-3 border">Lớp</th>
                    <th className="p-3 border">Môn học</th>
                    <th className="p-3 border">Giáo viên phụ trách</th>
                  </tr>
                </thead>
                <tbody>
                  {tkbChung.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="p-3 border font-medium">{item.thu}</td>
                      <td className="p-3 border text-center">{item.tiet}</td>
                      <td className="p-3 border font-semibold text-blue-600">{item.lop}</td>
                      <td className="p-3 border">{item.mon_hoc}</td>
                      <td className="p-3 border font-medium text-green-700">{item.giao_vien}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Nội dung Tab TKB Theo Giáo Viên */}
          {activeTab === 'giaovien' && (
            <div>
              <div className="mb-4 flex items-center gap-3">
                <label className="font-medium text-gray-700">Chọn giáo viên:</label>
                <select
                  value={selectedTeacher}
                  onChange={(e) => setSelectedTeacher(e.target.value)}
                  className="p-2 border rounded-md bg-white min-w-[250px]"
                >
                  {danhSachGiaoVien.map((gv, idx) => (
                    <option key={idx} value={gv}>{gv}</option>
                  ))}
                </select>
              </div>

              <div className="overflow-x-auto border rounded-lg">
                <table className="w-full text-left border-collapse text-sm">
                  <thead className="bg-green-50">
                    <tr>
                      <th className="p-3 border">Thứ</th>
                      <th className="p-3 border">Tiết</th>
                      <th className="p-3 border">Lớp giảng dạy</th>
                      <th className="p-3 border">Môn học</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tkbGiaoVien.length > 0 ? (
                      tkbGiaoVien.map((item, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="p-3 border font-medium">{item.thu}</td>
                          <td className="p-3 border text-center">{item.tiet}</td>
                          <td className="p-3 border font-semibold text-blue-600">{item.lop}</td>
                          <td className="p-3 border font-medium text-red-600">{item.mon_hoc}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" className="p-4 text-center text-gray-500">
                          Không có tiết dạy nào cho giáo viên này trong đợt TKB này.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
