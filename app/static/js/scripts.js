document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded and parsed");

  function createChart(ctx, type, labels, data, label, options = {}) {
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
      existingChart.destroy();
      console.log(`Destroyed existing chart for canvas: ${ctx.id}`);
    }

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: type === "pie" || type === "doughnut" ? "top" : "bottom",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales:
        type === "bar" || type === "line"
          ? {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                  callback: function (value) {
                    if (Number.isInteger(value)) {
                      return value;
                    }
                  },
                },
              },
              x:
                type === "line"
                  ? {
                      type: "time",
                      time: {
                        unit: "day",
                        tooltipFormat: "PPpp",
                        displayFormats: {
                          day: "MMM d",
                        },
                      },
                      title: {
                        display: true,
                        text: "Date",
                      },
                    }
                  : {},
            }
          : {},
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
      new Chart(ctx, {
        type: type,
        data: {
          labels: labels,
          datasets: [
            {
              label: label,
              data: data,
              backgroundColor:
                type === "pie" || type === "doughnut" || type === "bar"
                  ? generateColors(labels.length)
                  : undefined,
              borderColor: type === "line" ? "#0d6efd" : undefined,
              tension: type === "line" ? 0.1 : undefined,
            },
          ],
        },
        options: finalOptions,
      });
      console.log(`Chart created successfully for canvas: ${ctx.id}`);
    } catch (error) {
      console.error(`Error creating chart for canvas ${ctx.id}:`, error);
      const context = ctx.getContext("2d");
      context.clearRect(0, 0, ctx.width, ctx.height);
      context.fillStyle = "red";
      context.font = "16px Arial";
      context.textAlign = "center";
      context.fillText(
        "Error loading chart data",
        ctx.width / 2,
        ctx.height / 2,
      );
    }
  }

  function generateColors(count) {
    const colors = [
      "rgba(255, 99, 132, 0.7)",
      "rgba(54, 162, 235, 0.7)",
      "rgba(255, 206, 86, 0.7)",
      "rgba(75, 192, 192, 0.7)",
      "rgba(153, 102, 255, 0.7)",
      "rgba(255, 159, 64, 0.7)",
      "rgba(199, 199, 199, 0.7)",
      "rgba(83, 102, 255, 0.7)",
      "rgba(100, 255, 100, 0.7)",
    ];
    return colors.slice(0, count);
  }

  const statsDataElement = document.getElementById("stats-data");
  if (statsDataElement) {
    try {
      const stats = JSON.parse(statsDataElement.textContent);
      console.log("Stats data loaded:", stats);

      const eqCtx = document.getElementById("equipmentChart");
      if (eqCtx && stats.by_equipment) {
        createChart(
          eqCtx,
          "bar",
          stats.by_equipment.map((item) => item.equipment_type),
          stats.by_equipment.map((item) => item.count),
          "# Violations",
        );
      } else {
        console.warn("Equipment chart canvas or data not found.");
      }

      const sevCtx = document.getElementById("severityChart");
      if (sevCtx && stats.by_severity) {
        createChart(
          sevCtx,
          "pie",
          stats.by_severity.map((item) => item.severity),
          stats.by_severity.map((item) => item.count),
          "Violations by Severity",
        );
      } else {
        console.warn("Severity chart canvas or data not found.");
      }

      const locCtx = document.getElementById("locationChart");
      if (locCtx && stats.by_location) {
        const topLocations = stats.by_location.slice(0, 10); // Show top 10
        createChart(
          locCtx,
          "bar",
          topLocations.map((item) => item.location),
          topLocations.map((item) => item.count),
          "# Violations",
        );
      } else {
        console.warn("Location chart canvas or data not found.");
      }

      const statusCtx = document.getElementById("statusChart");
      if (statusCtx && stats.by_status) {
        createChart(
          statusCtx,
          "doughnut",
          stats.by_status.map((item) => item.status),
          stats.by_status.map((item) => item.count),
          "Violations by Status",
        );
      } else {
        console.warn("Status chart canvas or data not found.");
      }

      const trendCtx = document.getElementById("dailyTrendChart");
      if (trendCtx && stats.daily_trend) {
        const trendData = stats.daily_trend.map((item) => ({
          x: new Date(item.day),
          y: item.count,
        }));
        createChart(
          trendCtx,
          "line",
          trendData.map((d) => d.x),
          trendData.map((d) => d.y),
          "Daily Violations",
        );
      } else {
        console.warn("Daily trend chart canvas or data not found.");
      }
    } catch (e) {
      console.error("Error parsing stats data or creating charts:", e);
      [
        "equipmentChart",
        "severityChart",
        "locationChart",
        "statusChart",
        "dailyTrendChart",
      ].forEach((id) => {
        const canvas = document.getElementById(id);
        if (canvas) {
          const context = canvas.getContext("2d");
          context.clearRect(0, 0, canvas.width, canvas.height);
          context.fillStyle = "red";
          context.font = "16px Arial";
          context.textAlign = "center";
          context.fillText(
            "Error loading chart data",
            canvas.width / 2,
            canvas.height / 2,
          );
        }
      });
    }
  } else {
    console.warn("Stats data element (#stats-data) not found.");
  }
});
