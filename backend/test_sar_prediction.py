import sqlite3
from sar_drift import predict_drift

conn = sqlite3.connect("orca_cache.db")

incident = conn.execute(
    """
    INSERT INTO sar_incidents
    (status, last_known_latitude, last_known_longitude)
    VALUES (?, ?, ?)
    """,
    ("active", 19.0760, 72.8777),
)

incident_id = incident.lastrowid

result = predict_drift(
    19.0760,
    72.8777,
    1.0,
    90.0,
    10.0,
    180.0,
    2.0,
)

conn.execute(
    """
    INSERT INTO sar_predictions
    (incident_id, predicted_latitude, predicted_longitude, uncertainty_km)
    VALUES (?, ?, ?, ?)
    """,
    (
        incident_id,
        result["predicted_latitude"],
        result["predicted_longitude"],
        result["uncertainty_km"],
    ),
)

conn.commit()

print({
    "incident_id": incident_id,
    "prediction": result,
})

conn.close()
