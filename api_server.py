from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse

app = FastAPI(title="Drone App Manager")
drone_repo = None
parcel_repo = None

def set_repo(repo_drone, repo_parcel):
    global drone_repo, parcel_repo
    drone_repo = repo_drone
    parcel_repo = repo_parcel


def get_base_html(title, content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta http-equiv="refresh" content="5"> 
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #121212; color: #e0e0e0; padding: 0; margin: 0; }}
            
            /* Navigation Bar */
            .navbar {{ background-color: #1e1e1e; padding: 15px; text-align: center; border-bottom: 2px solid #333; position: sticky; top: 0; z-index: 100; }}
            .nav-btn {{ text-decoration: none; color: #888; padding: 10px 20px; font-weight: bold; border-radius: 20px; margin: 0 5px; transition: 0.3s; }}
            .nav-btn.active {{ background-color: #2196F3; color: white; }}
            .nav-btn:hover {{ background-color: #333; }}

            .container {{ padding: 20px; max-width: 800px; margin: 0 auto; }}
            .card {{ background: #1e1e1e; border-radius: 12px; padding: 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3); overflow: hidden; }}
            
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #252525; text-align: left; color: #aaa; padding: 12px 15px; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }}
            td {{ padding: 15px; border-bottom: 1px solid #2c2c2c; vertical-align: middle; font-size: 0.95em; }}
            tr:last-child td {{ border-bottom: none; }}
            
            .badge {{ padding: 5px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; color: white; display: inline-block; }}
            .badge-yellow {{ background-color: #FFC107; color: black; }} /* Pending */
            .badge-blue {{ background-color: #2196F3; }} /* Assigned */
            .badge-green {{ background-color: #4CAF50; }} /* Delivered */
            .badge-gray {{ background-color: #666; }} /* Unknown */

            .detail-text {{ display: block; font-size: 0.8em; color: #888; margin-top: 4px; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <a href="/drones" class="nav-btn {'active' if 'Drone' in title else ''}"> Drones</a>
            <a href="/parcels" class="nav-btn {'active' if 'Parcel' in title else ''}"> Parcels</a>
            <a href="/parcels_history" class="nav-btn {'active' if 'Parcel History' in title else ''}"> Parcels History</a>
        </div>
        <div class="container">
            <div class="card">
                {content}
            </div>
            <p style="text-align: center; color: #555; font-size: 0.8em; margin-top: 20px;">
                Live Connection • Auto-Refresh (5s)
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/drones", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def drone_status():
    if drone_repo is None:
        return "<h1> System Offline (Repo not connected) <h1>"
    
    drones = drone_repo.list_the_drones()
    rows_html = ""
    for drone in drones:
        status_color = "#4CAF50" if drone.get_status() == "IDLE" else "#FF5722"
        battery = drone.get_battery_level()
        batt_color = "#4CAF50" if battery > 50 else ("#FFC107" if battery > 20 else "#F44336")

        rows_html += f"""
        <tr>
            <td><strong>#{drone.get_id()}</strong></td>
            <td>{drone.get_model_type()}</td>
            <td><span style="background-color: {status_color}; padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.9em;">{drone.get_status()}</span></td>
            <td>
                <div style="background: #333; width: 100%; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div style="width: {battery}%; height: 100%; background: {batt_color}; text-align: center; line-height: 20px; font-size: 0.8em; color: black; font-weight: bold;">
                        {battery}%
                    </div>
                </div>
            </td>
        </tr>
        """

    content = f"<table><thead><tr><th>ID</th><th>Model</th><th>Status</th><th>Battery</th></tr></thead><tbody>{rows_html}</tbody></table>"
    return get_base_html("Drone Status", content)
    

@app.get("/parcels", response_class=HTMLResponse)
def parcels_status():
    if parcel_repo is None:
        return "<h1> System Offline (Repo not connected) <h1>"
    
    parcels = parcel_repo.get_parcels()
    rows_html = ""
    for parcel in parcels:
        if parcel.get_status() != "DELIVERED":
            status = parcel.get_status()
            if status == "PENDING": badge_class = "badge-yellow"
            elif status == "ASSIGNED": badge_class = "badge-blue"
            else: badge_class = "badge-gray"

            rows_html += f"""
            <tr>
                <td style="font-weight: bold; color: #fff;">#{parcel.get_id()}</td>
                <td>
                    <span class="badge {badge_class}">{status}</span>
                </td>
                <td>
                    {parcel.get_weight()}kg
                    <span class="detail-text">Priority: Standard</span>
                </td>
                <td>
                    <span style="color: #ddd;">{parcel.get_delivery_address()[:15]}...</span>
                    <span class="detail-text">{parcel.get_distance()} km</span>
                </td>
            </tr>
            """

    content = f"<table><thead><tr><th>ID</th><th>Status</th><th>Details</th><th>Dest</th></tr></thead><tbody>{rows_html}</tbody></table>"
    return get_base_html("Parcel Manifest", content)
        
@app.get("/parcels_history", response_class=HTMLResponse)
def parcels_history():
    if parcel_repo is None:
        return "<h1> System Offline (Repo not connected) <h1>"
    
    parcels = parcel_repo.get_delivered_parcels()
    rows_html = ""
    for parcel in parcels:

        badge_class = "badge-green"

        rows_html += f"""
            <tr>
            <td style="font-weight: bold; color: #fff;">#{parcel.get_id()}</td>
            <td>
             <span class="badge {badge_class}">{parcel.get_status()}</span>
            </td>
            <td>
            {parcel.get_weight()}kg
             <span class="detail-text">Priority: Standard</span>
            </td>
            <td>
            <span style="color: #ddd;">{parcel.get_delivery_address()[:15]}...</span>
            <span class="detail-text">{parcel.get_distance()} km</span>
                </td>
            </tr>
            """
        
    content = f"<table><thead><tr><th>ID</th><th>Status</th><th>Details</th><th>Dest</th></tr></thead><tbody>{rows_html}</tbody></table>"
    return get_base_html("Parcel History", content)

def start_server_thread():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
    

