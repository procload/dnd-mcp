# D&D Knowledge Navigator - Example Queries and Responses

This document provides examples of queries you can ask the D&D Knowledge Navigator and the types of responses you can expect. These examples demonstrate the capabilities of the system and how information is presented.

## Spell Queries

### Query: "Tell me about the Fireball spell"

**Expected Response:**

```
# Fireball

*3rd-level evocation*

**Casting Time:** 1 action
**Range:** 150 feet
**Components:** V, S, M (a tiny ball of bat guano and sulfur)
**Duration:** Instantaneous

A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.

The fire spreads around corners. It ignites flammable objects in the area that aren't being worn or carried.

**At Higher Levels:** When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.

---

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/spells/fireball
Confidence: High (Direct API match)
Relevance: 0.98
```

### Query: "What level is Counterspell?"

**Expected Response:**

```
Counterspell is a 3rd-level abjuration spell.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/spells/counterspell
Confidence: High (Direct API match)
Relevance: 0.95
```

## Monster Queries

### Query: "What is the AC of an Adult Red Dragon?"

**Expected Response:**

```
An Adult Red Dragon has an Armor Class (AC) of 19.

The Adult Red Dragon's AC is derived from its natural armor.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/monsters/adult-red-dragon
Confidence: High (Direct API match)
Relevance: 0.97
```

### Query: "Show me the stat block for a Beholder"

**Expected Response:**

```
# Beholder

*Large aberration, lawful evil*

**Armor Class:** 18 (natural armor)
**Hit Points:** 180 (19d10 + 76)
**Speed:** 0 ft., fly 20 ft. (hover)

| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| 10 (0) | 14 (+2) | 18 (+4) | 17 (+3) | 15 (+2) | 17 (+3) |

**Saving Throws:** Int +8, Wis +7, Cha +8
**Skills:** Perception +12
**Condition Immunities:** Prone
**Senses:** Darkvision 120 ft., passive Perception 22
**Languages:** Deep Speech, Undercommon
**Challenge:** 13 (10,000 XP)

## Special Traits

**Antimagic Cone:** The beholder's central eye creates an area of antimagic, as in the antimagic field spell, in a 150-foot cone. At the start of each of its turns, the beholder decides which way the cone faces and whether the cone is active. The area works against the beholder's own eye rays.

**Death Throes:** When the beholder dies, the magical energy within it explodes, and each creature within 30 feet of it must make a DC 14 Dexterity saving throw, taking 21 (6d6) force damage on a failed save, or half as much damage on a successful one.

## Actions

**Bite:** Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 14 (4d6) piercing damage.

**Eye Rays:** The beholder shoots three of the following magical eye rays at random (reroll duplicates), choosing one to three targets it can see within 120 feet of it:

1. **Charm Ray:** The targeted creature must succeed on a DC 16 Wisdom saving throw or be charmed by the beholder for 1 hour, or until the beholder harms the creature.

2. **Paralyzing Ray:** The targeted creature must succeed on a DC 16 Constitution saving throw or be paralyzed for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

3. **Fear Ray:** The targeted creature must succeed on a DC 16 Wisdom saving throw or be frightened for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

4. **Slowing Ray:** The targeted creature must succeed on a DC 16 Dexterity saving throw. On a failed save, the target's speed is halved for 1 minute. In addition, the creature can't take reactions, and it can take either an action or a bonus action on its turn, not both. The creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

5. **Enervation Ray:** The targeted creature must make a DC 16 Constitution saving throw, taking 36 (8d8) necrotic damage on a failed save, or half as much damage on a successful one.

6. **Telekinetic Ray:** If the target is a creature, it must succeed on a DC 16 Strength saving throw or the beholder moves it up to 30 feet in any direction. It is restrained by the ray's telekinetic grip until the start of the beholder's next turn or until the beholder is incapacitated.

7. **Sleep Ray:** The targeted creature must succeed on a DC 16 Wisdom saving throw or fall asleep and remain unconscious for 1 minute. The target awakens if it takes damage or another creature takes an action to wake it. This ray has no effect on constructs and undead.

8. **Petrification Ray:** The targeted creature must make a DC 16 Dexterity saving throw. On a failed save, the creature begins to turn to stone and is restrained. It must repeat the saving throw at the end of its next turn. On a success, the effect ends. On a failure, the creature is petrified until freed by the greater restoration spell or other magic.

9. **Disintegration Ray:** If the target is a creature, it must succeed on a DC 16 Dexterity saving throw or take 45 (10d8) force damage. If this damage reduces the creature to 0 hit points, its body becomes a pile of fine gray dust. If the target is a Large or smaller nonmagical object or creation of magical force, it is disintegrated without a saving throw. If the target is a Huge or larger object or creation of magical force, this ray disintegrates a 10-foot cube of it.

10. **Death Ray:** The targeted creature must succeed on a DC 16 Dexterity saving throw or take 55 (10d10) necrotic damage. The target dies if the ray reduces it to 0 hit points.

## Legendary Actions

The beholder can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The beholder regains spent legendary actions at the start of its turn.

**Eye Ray:** The beholder uses one random eye ray.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/monsters/beholder
Confidence: High (Direct API match)
Relevance: 0.99
```

## Class Queries

### Query: "What are the features of a level 5 Barbarian?"

**Expected Response:**

```
# Barbarian Class Features (Level 5)

A 5th-level Barbarian has the following class features:

## Hit Points
- **Hit Dice:** 5d12
- **Hit Points at 5th Level:** 5d12 + 5 × your Constitution modifier
- **Hit Points per Level after 5th:** 1d12 (or 7) + your Constitution modifier

## Proficiencies
- **Armor:** Light armor, medium armor, shields
- **Weapons:** Simple weapons, martial weapons
- **Tools:** None
- **Saving Throws:** Strength, Constitution
- **Skills:** Choose two from Animal Handling, Athletics, Intimidation, Nature, Perception, and Survival

## Class Features

### Rage (2/day)
In battle, you fight with primal ferocity. On your turn, you can enter a rage as a bonus action. While raging, you gain the following benefits if you aren't wearing heavy armor:
- You have advantage on Strength checks and Strength saving throws.
- When you make a melee weapon attack using Strength, you gain a +2 bonus to the damage roll.
- You have resistance to bludgeoning, piercing, and slashing damage.

Your rage lasts for 1 minute. It ends early if you are knocked unconscious or if your turn ends and you haven't attacked a hostile creature since your last turn or taken damage since then. You can also end your rage on your turn as a bonus action.

At 5th level, you can rage 3 times per day.

### Unarmored Defense
While you are not wearing any armor, your Armor Class equals 10 + your Dexterity modifier + your Constitution modifier. You can use a shield and still gain this benefit.

### Reckless Attack
Starting at 2nd level, you can throw aside all concern for defense to attack with fierce desperation. When you make your first attack on your turn, you can decide to attack recklessly. Doing so gives you advantage on melee weapon attack rolls using Strength during this turn, but attack rolls against you have advantage until your next turn.

### Danger Sense
At 2nd level, you gain an uncanny sense of when things nearby aren't as they should be, giving you an edge when you dodge away from danger. You have advantage on Dexterity saving throws against effects that you can see, such as traps and spells. To gain this benefit, you can't be blinded, deafened, or incapacitated.

### Primal Path
At 3rd level, you choose a path that shapes the nature of your rage. Your choice grants you features at 3rd level and again at 6th, 10th, and 14th levels.

### Ability Score Improvement
When you reach 4th level, you can increase one ability score of your choice by 2, or you can increase two ability scores of your choice by 1. As normal, you can't increase an ability score above 20 using this feature.

### Extra Attack
Beginning at 5th level, you can attack twice, instead of once, whenever you take the Attack action on your turn.

### Fast Movement
Starting at 5th level, your speed increases by 10 feet while you aren't wearing heavy armor.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/classes/barbarian
Confidence: High (Direct API match)
Relevance: 0.96
```

## Equipment Queries

### Query: "How much damage does a Greatsword do?"

**Expected Response:**

```
A Greatsword deals 2d6 slashing damage.

**Additional Properties:**
- **Category:** Martial Melee Weapon
- **Cost:** 50 gp
- **Weight:** 6 lb.
- **Properties:** Heavy, Two-Handed

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/equipment/greatsword
Confidence: High (Direct API match)
Relevance: 0.98
```

## Verification Queries

### Query: "Verify if Fireball is a 3rd level spell"

**Expected Response:**

```
✅ Verified: Fireball is indeed a 3rd level spell.

I checked the D&D 5e API and found that Fireball is classified as a 3rd-level evocation spell.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/spells/fireball
Confidence: High (Direct API match)
Relevance: 0.99
```

### Query: "Is it true that dragons have immunity to their breath weapon damage type?"

**Expected Response:**

```
✅ Verified: Dragons typically have immunity to their breath weapon damage type.

I checked several dragon entries in the D&D 5e API:
- Red dragons have immunity to fire damage (their breath weapon deals fire damage)
- Blue dragons have immunity to lightning damage (their breath weapon deals lightning damage)
- Green dragons have immunity to poison damage (their breath weapon deals poison damage)
- White dragons have immunity to cold damage (their breath weapon deals cold damage)
- Black dragons have immunity to acid damage (their breath weapon deals acid damage)

This pattern holds true across chromatic dragons, confirming that dragons generally have immunity to their breath weapon damage type.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/monsters/adult-red-dragon, /api/monsters/adult-blue-dragon, etc.
Confidence: High (Multiple direct API matches)
Relevance: 0.97
```

## API Health Check

### Query: "Check if the D&D API is working"

**Expected Response:**

```
✅ The D&D 5e API is operational.

I checked the following endpoints:
- Base API: Available
- Spells endpoint: 319 spells available
- Monsters endpoint: 334 monsters available
- Classes endpoint: 12 classes available

All critical endpoints are responding correctly.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api, /api/spells, /api/monsters, /api/classes
Confidence: High (Direct API check)
Relevance: 1.0
```

## Query Enhancement Examples

### Query: "What is the AC of a dragon?"

**Enhanced Query:** "What is the armor class of a dragon?"

**Expected Response:**

```
Dragons have different Armor Class (AC) values depending on their type and age. Here are some examples:

- Adult Red Dragon: AC 19 (natural armor)
- Adult Blue Dragon: AC 19 (natural armor)
- Adult Green Dragon: AC 19 (natural armor)
- Adult Black Dragon: AC 19 (natural armor)
- Adult White Dragon: AC 18 (natural armor)
- Ancient Red Dragon: AC 22 (natural armor)
- Young Red Dragon: AC 18 (natural armor)
- Wyrmling Red Dragon: AC 17 (natural armor)

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/monsters?name=dragon
Confidence: High (Direct API match)
Relevance: 0.92
Query Enhancement: Expanded "AC" to "armor class"
```

### Query: "Tell me about firball"

**Enhanced Query:** "Tell me about fireball"

**Expected Response:**

```
# Fireball

*3rd-level evocation*

**Casting Time:** 1 action
**Range:** 150 feet
**Components:** V, S, M (a tiny ball of bat guano and sulfur)
**Duration:** Instantaneous

A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.

The fire spreads around corners. It ignites flammable objects in the area that aren't being worn or carried.

**At Higher Levels:** When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.

**Source Attribution:**
Source: D&D 5e API
Endpoint: /api/spells/fireball
Confidence: High (Direct API match)
Relevance: 0.95
Query Enhancement: Corrected "firball" to "fireball"
```
