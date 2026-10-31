# Power BI Development

```
development/   Power BI projects (jh_crowd_strike, pbi_report_theme_template)
python_scripts/ Reusable automation scripts
scratch/       Throwaway scripts (git-ignored)
.agents/       Agent rules & workflows
```

## Setup
```bash
cp .env.template .env            # then edit values
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python python_scripts/setup_skills.py   # clones microsoft/skills-for-fabric
```

The AI agent follows `.agents/AGENTS.md` and will download the
[Microsoft Skills for Fabric](https://github.com/microsoft/skills-for-fabric) repo automatically if `skills-for-fabric/` is missing.
