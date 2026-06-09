function newsCards() {
  return (window.LTN_NEWS || []).map(function (item) {
    return '<article class="card news-card"><p class="eyebrow">' + item.date + '</p><h3>' + item.title + '</h3><p>' + item.summary + '</p><details><summary>Đọc nội dung</summary><p>' + (item.content || item.summary) + '</p></details></article>';
  }).join("");
}

function newsManagementPanel() {
  return '<form class="card form-grid management-form"><h3>Đăng bài viết mới</h3><input placeholder="Tiêu đề bài viết"><input type="date"><textarea placeholder="Tóm tắt bài viết"></textarea><textarea placeholder="Nội dung chi tiết"></textarea><button type="button" data-save-row>Đăng bài viết</button></form>' +
    '<div class="grid grid-3">' + (window.LTN_NEWS || []).map(function (item) {
      return '<article class="card news-card"><p class="eyebrow">' + item.date + '</p><h3>' + item.title + '</h3><p>' + item.summary + '</p><details open><summary>Nội dung bài viết</summary><p>' + (item.content || item.summary) + '</p></details><div class="row-actions"><button class="btn secondary" data-save-row>Chỉnh sửa</button><button class="btn ghost" data-delete-row>Xóa</button></div></article>';
    }).join("") + '</div>';
}
