<!DOCTYPE html>
<html>
  <head>
    <title>Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/style.css') }}"
    />
    <style>
      :root {
        --primary-color: #2c3e50;
        --secondary-color: #e74c3c;
        --accent-color: #091d2b;
        --light-color: #ecf0f1;
        --dark-color: #cadef2;
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
      }
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: var(--accent-color);
        color: white;
      }

      .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
      }

      /* Header Styles */
      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
      }

      .header-title {
        font-size: 18px;
        font-weight: bold;
      }

      .header-logo {
        display: flex;
        align-items: center;
      }

      .header-icon {
        background-color: #536279;
        border-radius: 8px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
      }

      .header-right {
        display: flex;
        align-items: center;
      }

      .user-icon {
        width: 32px;
        height: 32px;
        background-color: #536279;
        border-radius: 50%;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
      }

      /* Main Content Layout */
      .main-content {
        display: flex;
      }

      /* Sidebar Styles */
      .sidebar {
        width: 60px;
        background-color: #556f74;
        padding: 15px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 25px;
        border-radius: 10px;
        margin-right: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      }

      .sidebar-icon {
        color: white;
        font-size: 24px;
        cursor: pointer;
      }

      .sidebar-icon.active {
        color: #000;
      }

      .content-area {
        flex: 1;
      }

      /* Score and Metrics Section */
      .score-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-bottom: 20px;
      }

      .score-card {
        background-color: #556f74;
        border-radius: 10px;
        padding: 20px;
        color: white;
        flex: 1;
        min-width: 200px;
        position: relative;
        overflow: hidden;
      }

      .score-gauge {
        position: relative;
        width: 140px;
        height: 140px;
        margin-right: 20px;
      }

      .score-gauge svg {
        transform: rotate(-90deg);
      }

      .score-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 42px;
        font-weight: bold;
      }

      .score-title {
        font-size: 16px;
        margin-top: 5px;
        opacity: 0.8;
      }

      .score-details {
        margin-top: 20px;
      }

      .score-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
      }

      .score-item-label {
        font-size: 14px;
        opacity: 0.8;
      }

      .score-item-value {
        font-weight: 600;
      }

      .score-item-bar {
        height: 5px;
        background-color: #333;
        border-radius: 5px;
        margin-top: 5px;
        position: relative;
      }

      .score-item-fill {
        height: 100%;
        border-radius: 5px;
        background-color: #4caf50;
      }

      /* Highlighted Videos Section */
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
      }

      .section-title {
        font-size: 16px;
        font-weight: bold;
      }

      .view-all {
        font-size: 14px;
        color: white;
        text-decoration: none;
      }

      .videos-container {
        display: flex;
        gap: 15px;
        overflow-x: auto;
        padding-bottom: 10px;
      }

      .video-card {
        width: 180px;
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      }

      .video-thumbnail {
        width: 100%;
        height: 100px;
        object-fit: cover;
        display: block;
      }

      .video-details {
        padding: 10px;
      }

      .video-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 5px;
        color: #000;
      }

      .video-info {
        font-size: 12px;
        color: rgb(47, 41, 41);
        display: flex;
        justify-content: space-between;
      }

      /* Incidents Section */
      .incidents-container {
        margin-top: 30px;
      }

      .incidents-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
      }

      .incidents-title {
        font-size: 16px;
        font-weight: bold;
      }

      .incidents-count {
        font-size: 24px;
        font-weight: bold;
      }

      .incidents-chart {
        background-color: #c0d8dc;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      }

      .chart-bars {
        display: flex;
        align-items: flex-end;
        height: 60px;
        gap: 2px;
      }

      .chart-bar {
        background-color: #000;
        flex: 1;
      }

      /* Activity Sidebar */
      .activity-sidebar {
        width: 300px;
        background-color: #556f74;
        border-radius: 10px;
        color: white;
        padding: 20px;
        margin-left: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      }

      .activity-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
      }

      .activity-title {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 5px;
        color: #000;
      }

      .activity-count {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
        color: #000;
      }

      .activity-subtitle {
        font-size: 12px;
        color: #000;
      }

      .activity-list {
        margin-top: 30px;
      }

      .activity-list-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 15px;
      }

      .activity-item {
        display: flex;
        margin-bottom: 15px;
        align-items: flex-start;
      }

      .activity-icon {
        width: 24px;
        height: 24px;
        background-color: #f1f1f1;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        flex-shrink: 0;
      }

      .activity-content {
        flex: 1;
      }

      .activity-text {
        font-size: 13px;
        line-height: 1.4;
      }

      .activity-time {
        font-size: 12px;
        color: #666;
        margin-top: 3px;
      }
    </style>
  </head>

  <body>
    <div class="container">
      <div class="header">
        <div class="header-logo">
          <div class="header-title">Dashboard</div>
        </div>
        <div class="header-right">
          <div class="user-icon">Hh</div>
        </div>
      </div>

      <div class="main-content">
        <div class="sidebar">
            <a href="index.html" class="sidebar-icon active">🏠</a>
            <a href="#analytics" class="sidebar-icon">📊</a>
            <a href="#reports" class="sidebar-icon">📋</a>
            <a href="#progress" class="sidebar-icon">📈</a>
          </div>

        <div id ="analytics" class="content-area">
          <div class="score-container">
            <div class="score-card">
              <div style="display: flex">
                <div class="score-gauge">
                  <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle
                      cx="70"
                      cy="70"
                      r="60"
                      fill="none"
                      stroke="#333"
                      stroke-width="10"
                    />
                    <circle
                      cx="70"
                      cy="70"
                      r="60"
                      fill="none"
                      stroke="#4CAF50"
                      stroke-width="10"
                      stroke-dasharray="377"
                      stroke-dashoffset="109"
                    />
                  </svg>
                  <div class="score-value">71</div>
                </div>
                <div style="flex: 1">
                  <div class="score-title">Voxel Site Score</div>

                  <div class="score-details">
                    <div class="score-item">
                      <div class="score-item-label">Improper Lifting</div>
                      <div class="score-item-value">20</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 20%; background-color: #ff6b6b"
                      ></div>
                    </div>

                    <div class="score-item">
                      <div class="score-item-label">Overreaching</div>
                      <div class="score-item-value">43</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 43%; background-color: #ff9f43"
                      ></div>
                    </div>

                    <div class="score-item">
                      <div class="score-item-label">No Stop at Aisle</div>
                      <div class="score-item-value">59</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 59%; background-color: #feca57"
                      ></div>
                    </div>

                    <div class="score-item">
                      <div class="score-item-label">
                        No Stop at Intersection
                      </div>
                      <div class="score-item-value">71</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 71%; background-color: #1dd1a1"
                      ></div>
                    </div>

                    <div class="score-item">
                      <div class="score-item-label">No Red Zone</div>
                      <div class="score-item-value">86</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 86%; background-color: #2ecc71"
                      ></div>
                    </div>

                    <div class="score-item">
                      <div class="score-item-label">Safety Vest</div>
                      <div class="score-item-value">99</div>
                    </div>
                    <div class="score-item-bar">
                      <div
                        class="score-item-fill"
                        style="width: 99%; background-color: #10ac84"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="section-header">
            <div class="section-title">Highlighted Videos</div>
            <a href="#" class="view-all">View All</a>
          </div>

          <div class="videos-container">
            <div class="video-card">
              <video autoplay loop muted playsinline class="video-thumbnail">
                <source
                  src="../static/images/unsafelift.webm"
                  type="video/webm"
                />
              </video>
              <div class="video-details">
                <div class="video-title">Improper Lifting</div>
                <div class="video-info">
                  <span>Aisle 3 Zone 4</span>
                  <span>2 days ago</span>
                </div>
              </div>
            </div>

            <div class="video-card">
              <video autoplay loop muted playsinline class="video-thumbnail">
                <source
                  src="../static/images/nearmiss.webm"
                  type="video/webm"
                />
              </video>
              <div class="video-details">
                <div class="video-title">Near Miss</div>
                <div class="video-info">
                  <span>Forklift Zone</span>
                  <span>10 hrs ago</span>
                </div>
              </div>
            </div>

            <div class="video-card">
              <video autoplay loop muted playsinline class="video-thumbnail">
                <source src="../static/images/loading.webm" type="video/webm" />
              </video>
              <div class="video-details">
                <div class="video-title">Blocked Aisle</div>
                <div class="video-info">
                  <span>Loading Zone 3</span>
                  <span>2 days ago</span>
                </div>
              </div>
            </div>
          </div>

          <div id="reports"  class="incidents-container">
            <div class="incidents-header">
              <div>
                <div class="incidents-title">All Incidents</div>
                <div class="incidents-count">771</div>
                <div class="video-info">Total Incidents · Last 30 days</div>
              </div>
              <div>
                <span style="color: white">+25%</span>
              </div>
            </div>

            <div class="incidents-chart">
              <div class="chart-bars">
                <!-- Generate 30 random height bars -->
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 45%"></div>
                <div class="chart-bar" style="height: 60%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 55%"></div>
                <div class="chart-bar" style="height: 80%"></div>
                <div class="chart-bar" style="height: 75%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 65%"></div>
                <div class="chart-bar" style="height: 45%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 60%"></div>
                <div class="chart-bar" style="height: 80%"></div>
                <div class="chart-bar" style="height: 70%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 45%"></div>
                <div class="chart-bar" style="height: 65%"></div>
                <div class="chart-bar" style="height: 55%"></div>
                <div class="chart-bar" style="height: 75%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 60%"></div>
              </div>
            </div>

            <div class="incidents-header">
              <div>
                <div class="incidents-title">Improper Lifting</div>
                <div class="incidents-count">456</div>
                <div class="video-info">Total Events · Last 30 days</div>
              </div>
              <div>
                <span style="color: white">+10%</span>
              </div>
            </div>

            <div class="incidents-chart">
              <div class="chart-bars">
                <!-- Generate 30 random height bars -->
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 45%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 80%"></div>
                <div class="chart-bar" style="height: 60%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 65%"></div>
                <div class="chart-bar" style="height: 55%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 75%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 55%"></div>
                <div class="chart-bar" style="height: 70%"></div>
                <div class="chart-bar" style="height: 60%"></div>
                <div class="chart-bar" style="height: 45%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 50%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 75%"></div>
                <div class="chart-bar" style="height: 65%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 55%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 45%"></div>
              </div>
            </div>

            <div class="incidents-header">
              <div>
                <div class="incidents-title">Overreaching</div>
                <div class="incidents-count">62</div>
                <div class="video-info">Total Events · Last 30 days</div>
              </div>
              <div>
                <span style="color: white">No change</span>
              </div>
            </div>

            <div class="incidents-chart">
              <div class="chart-bars">
                <!-- Generate 30 random height bars -->
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 10%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 10%"></div>
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 40%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 35%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 10%"></div>
                <div class="chart-bar" style="height: 25%"></div>
                <div class="chart-bar" style="height: 15%"></div>
                <div class="chart-bar" style="height: 20%"></div>
                <div class="chart-bar" style="height: 30%"></div>
                <div class="chart-bar" style="height: 25%"></div>
              </div>
            </div>
          </div>
        </div>

        <div id="progress" class="activity-sidebar">
          <div class="activity-card">
            <div class="activity-title">Assigned to me</div>
            <div class="activity-count">3</div>
            <div class="activity-subtitle">Unresolved</div>
          </div>

          <div class="activity-card">
            <div class="activity-title">Assigned to me</div>
            <div class="activity-count">53</div>
            <div class="activity-subtitle">Resolved</div>
          </div>

          <div class="activity-card">
            <div class="activity-title">Bookmarked</div>
            <div class="activity-count">23</div>
          </div>

          <div class="activity-list">
            <div class="activity-list-title">Recent Activity</div>

            <div class="activity-item">
              <div class="activity-icon">✓</div>
              <div class="activity-content">
                <div class="activity-text">
                  Overreaching event resolved by Alex
                </div>
                <div class="activity-time">2h ago</div>
              </div>
            </div>

            <div class="activity-item">
              <div class="activity-icon">💬</div>
              <div class="activity-content">
                <div class="activity-text">
                  Alex commented "Not sure" on a Improper Lifting event
                </div>
                <div class="activity-time">3h ago</div>
              </div>
            </div>

            <div class="activity-item">
              <div class="activity-icon">👤</div>
              <div class="activity-content">
                <div class="activity-text">
                  Brian Benson assigned a No Stop at Intersection event to Alex
                </div>
                <div class="activity-time">5h ago</div>
              </div>
            </div>

            <div class="activity-item">
              <div class="activity-icon">💬</div>
              <div class="activity-content">
                <div class="activity-text">
                  Brandon commented "Reopened" for a No Red Zone event
                </div>
                <div class="activity-time">10h ago</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>

