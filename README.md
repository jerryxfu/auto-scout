# auto-scout

```bash
pip install requests pandas openpyxl jinja2
```

Create a file called `constants.py` and add the following:

```python
TBA_API_KEY = "YOUR_API_KEY"
```

FRC auto scouting app

Possibly interesting data to collect:

Compare data with scouts data to find out how accurate the scouts are

### Teams

- Team number
- Team name

### Events

- OPR
- DPR
- CCWM

### Matches

- ALLIANCE
    - blue team numbers
    - red team numbers
- Score breakdown BLUE and RED
    - AUTO
        - ALLIANCE total CORAL count and points
        - robot 1,2,3 leave <<<
        - ALLIANCE total mobility points
        - ALLIANCE total points
        - REEF ALLIANCE count L1/2/3/4 A,B,C,D,E,F,G,H,I,J,K,L

    - TELEOP
        - CORAL placed
        - CORAL points
        - REEF ALLIANCE count L1/2/3/4 A,B,C,D,E,F,G,H,I,J,K,L
        - total points

    - ALLIANCE
        - net ALGAE count
        - wall ALGAE count (processor)
        - Ranking points
        - AUTO bonus achieved (auto RP) <<<
        - BARGE bonus achieved (barge RP) <<<
        - COOPERTITION criteria met
        - CORAL bonus achieved (reef RP) <<<
        - FOUL and TECH FOUL count and points
        - g206,g410,g418,g428 Penalty yes/no
    - END GAME
        - robot 1,2,3 Parked/DeepCage/ShallowCage/None <<<
        - ALLIANCE BARGE points
    - ALLIANCE score
    - Winning ALLIANCE
