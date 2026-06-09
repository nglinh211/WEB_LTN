(function () {
  function readJSON(id) {
    var node = document.getElementById(id);
    if (!node) return { labels: [], values: [] };
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return { labels: [], values: [] };
    }
  }

  function makeChart(canvasId, type, dataId, label, colors) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;
    var payload = readJSON(dataId);
    new Chart(canvas, {
      type: type,
      data: {
        labels: payload.labels || [],
        datasets: [{
          label: label,
          data: payload.values || [],
          backgroundColor: colors || ["#9B0036", "#F3E8DA", "#777777", "#F8E8EE", "#7D002C"],
          borderColor: "#9B0036",
          borderWidth: 2,
          tension: .35
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: type !== "bar" && type !== "line" } },
        scales: type === "doughnut" ? {} : { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }

  makeChart("revenueChart", "line", "revenue-data", "Doanh thu", ["rgba(155,0,54,.16)"]);
  makeChart("orderStatusChart", "doughnut", "status-data", "Đơn hàng");
  makeChart("categoryChart", "bar", "category-data", "Sản phẩm");
  makeChart("topProductChart", "bar", "top-product-data", "Đã bán");
  makeChart("inventoryCategoryChart", "bar", "inventory-category-data", "Tồn kho");
  makeChart("inventoryLowChart", "bar", "inventory-low-data", "Sản phẩm sắp hết");
  makeChart("inventoryTopChart", "bar", "inventory-top-data", "Tồn kho");
  makeChart("staffOrderChart", "bar", "staff-order-data", "Đơn hàng");
  makeChart("staffRevenueChart", "line", "staff-revenue-data", "Doanh thu", ["rgba(155,0,54,.16)"]);
  makeChart("staffCustomerChart", "bar", "staff-customer-data", "Khách hàng mới");
})();
