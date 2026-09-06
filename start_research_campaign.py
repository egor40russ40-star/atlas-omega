import sys

sys.path.insert(0, "app/src")

from omega_analytics.research_launcher import FirstResearchLauncher

campaign = {
    "name": "RESEARCH_CAMPAIGN_001",
    "mode": "RESEARCH_ONLY",
    "instruments": [
        "ROSN",
        "CNYRUBF",
        "SBER"
    ],
    "strategies": [
        "ROSN_HEDGE_V3",
        "CNYRUBF_BRM",
        "Trend_Pullback",
        "Breakout_Retest"
    ]
}

launcher = FirstResearchLauncher(campaign)
print(launcher.start())
