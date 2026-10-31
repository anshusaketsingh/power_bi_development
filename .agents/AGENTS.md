<RULE[python_scripts_organization]>
All scratch scripts will be put in the `scratch/` folder, and all reusable Python scripts will be put in the `python_scripts/` folder.
</RULE[python_scripts_organization]>

<RULE[project_bootstrap]>
Before any Power BI work, verify the environment:
1. If `.env` is missing, copy `.env.template` to `.env` and ask the user to fill in values.
2. If `venv/` is missing: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
3. If the `skills-for-fabric/` folder (see `SKILLS_PATH` in `.env`) is missing or empty, download Microsoft's skills with
   `source venv/bin/activate && python python_scripts/setup_skills.py`
   (clones https://github.com/microsoft/skills-for-fabric.git), then read its `README.md`/`AGENTS.md` and relevant `skills/` before building.
4. Power BI projects live under `development/`.
</RULE[project_bootstrap]>
