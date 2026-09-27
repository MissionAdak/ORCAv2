def calculate_risk_score(
    wave_score: float,
    wind_score: float,
    weather_score: float,
    current_score: float,
    geofence_score: float,
    alert_score: float,
):
    """
    ORCA Environmental Risk Engine

    Each input score should be between 0 and 100.

    Weights:
    Wave      = 30%
    Wind      = 25%
    Weather   = 15%
    Current   = 10%
    Geofence  = 10%
    Alert     = 10%
    """

    scores = [
        wave_score,
        wind_score,
        weather_score,
        current_score,
        geofence_score,
        alert_score,
    ]

    if any(score < 0 or score > 100 for score in scores):
        raise ValueError("All risk scores must be between 0 and 100")

    risk_score = (
        wave_score * 0.30
        + wind_score * 0.25
        + weather_score * 0.15
        + current_score * 0.10
        + geofence_score * 0.10
        + alert_score * 0.10
    )

    risk_score = round(risk_score, 2)

    if risk_score <= 30:
        risk_level = "LOW"
        recommended_action = "Continue monitoring conditions"
    elif risk_score <= 60:
        risk_level = "MODERATE"
        recommended_action = "Exercise caution and monitor conditions"
    else:
        risk_level = "HIGH"
        recommended_action = "Prioritize safety and consider immediate response"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
    }