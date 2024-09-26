lst1 = lst1;
lst2 = lst2;
lst3 = lst3;
lst4 = lst4;
console.log(lst1)
console.log(lst1)
console.log(lst1)
console.log(lst1)
var lineChart = document.getElementById("lineChart").getContext("2d"),
  pieChart = document.getElementById("pieChart").getContext("2d"),
  barChart = document.getElementById("barChart").getContext("2d"),
  //var xx = document.getElementById('AcadSemester');


// lineChart
  myLineChart = new Chart(lineChart, {
    type: "line",
    data: {
      labels: lst1,
      datasets: [
        {
          label: "GPA Progress",
          borderColor: "#1d7af3",
          pointBorderColor: "#FFF",
          pointBackgroundColor: "#1d7af3",
          pointBorderWidth: 2,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 1,
          pointRadius: 4,
          backgroundColor: "transparent",
          fill: true,
          borderWidth: 2,
          data: lst2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      legend: {
        position: "bottom",
        labels: {
          padding: 10,
          fontColor: "#1d7af3",
        },
      },
      tooltips: {
        bodySpacing: 4,
        mode: "nearest",
        intersect: 0,
        position: "nearest",
        xPadding: 10,
        yPadding: 10,
        caretPadding: 10,
      },
      layout: {
        padding: { left: 15, right: 15, top: 15, bottom: 15 },
      },
    },
  });
var lineChartCanvas = $("#lineChart").get(0).getContext("2d");
var lineChart = new Chart(lineChartCanvas);

// BarChart
var myBarChart = new Chart(barChart, {
  type: "bar",
  data: {
    labels: lst1,
    datasets: [
      {
        label: "Semester Earned Hours",
        backgroundColor: "rgb(23, 125, 255)",
        borderColor: "rgb(23, 125, 255)",
        data: lst4,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      yAxes: [
        {
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
  },
});
// PieChart
myPieChart = new Chart(pieChart, {
  type: "pie",
  data: {
    datasets: [
      {
        data: lst3,
        backgroundColor: ["#1d7af3", "#35db67"],
        borderWidth: 0,
      },
    ],
    labels: ["Required Hours", "Earned Hours"],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: "bottom",
      labels: {
        fontColor: "rgb(154, 154, 154)",
        fontSize: 11,
        usePointStyle: true,
        padding: 20,
      },
    },
    pieceLabel: {
      mode: "value",
      fontColor: "white",
      fontSize: 14,
    },
    tooltips: false,
    layout: {
      padding: {
        left: 20,
        right: 20,
        top: 20,
        bottom: 20,
      },
    },
  },
});
