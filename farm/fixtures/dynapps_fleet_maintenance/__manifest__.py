{
    "name": "Dynapps Fleet Maintenance",
    "summary": "Plan and track preventive maintenance for fleet vehicles",
    "version": "16.0.1.0.0",
    "category": "Human Resources/Fleet",
    "author": "Dynapps",
    "website": "https://dynapps.es",
    "depends": ["fleet", "mail"],
    "data": [
        "security/fleet_maintenance_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "views/fleet_maintenance_views.xml",
    ],
    "installable": True,
    "application": False,
}
