import time
import sys
import random
import json
import os
from difflib import get_close_matches


def load_items(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def load_all_items():
    items = []
    for i in range(1, 10):
        file_path = f'list{i}.json'
        if os.path.exists(file_path):
            items.extend(load_items(file_path))
    return items


def load_mega_items():
    return load_items('listmega.json')


def find_item_by_name(items, item_name):
    special_cases = {
        "nidoran-m": "Nidoran-m",
        "nidoran-f": "Nidoran-f"
    }
    item_name = special_cases.get(item_name.lower(), item_name)
    for item in items:
        if item['Name'].lower() == item_name.lower():
            return item
    return None


def find_mega_version(non_mega_name, mega_items):
    mega_name = f"Mega {non_mega_name.capitalize()}"
    return find_item_by_name(mega_items, mega_name)


def randomnumber(min_val, max_val):
    return random.randint(min_val, max_val)


def slow_print(text, delay=0.0411):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def format_pokemon_details(pokemon):
    return (
        f"Name: {pokemon['Name']}\n"
        f"Pokedex #: {pokemon['Pokedex #']}\n"
        f"Type: {pokemon['Type']}\n"
        f"Abilities: {pokemon.get('Abilities', 'Unknown')}\n"
        f"HP: {pokemon['HP']}\n"
        f"Attack: {pokemon['Attack']}\n"
        f"Defense: {pokemon['Defense']}\n"
        f"Sp. Atk: {pokemon['Sp. Atk']}\n"
        f"Sp. Def: {pokemon['Sp. Def']}\n"
        f"Speed: {pokemon['Speed']}\n"
    )


type_effectiveness = {
    "Fire": ["Water", "Rock", "Ground"],
    "Water": ["Electric", "Grass"],
    "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
    "Electric": ["Ground"],
    "Ice": ["Fire", "Fighting", "Rock", "Steel"],
    "Fighting": ["Flying", "Psychic", "Fairy"],
    "Poison": ["Ground", "Psychic"],
    "Ground": ["Water", "Ice", "Grass"],
    "Flying": ["Electric", "Ice", "Rock"],
    "Psychic": ["Bug", "Ghost", "Dark"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Rock": ["Water", "Grass", "Fighting", "Ground", "Steel"],
    "Ghost": ["Ghost", "Dark"],
    "Dragon": ["Ice", "Dragon", "Fairy"],
    "Dark": ["Fighting", "Bug", "Fairy"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"],
}

type_resistances = {
    "Fire": ["Fire", "Grass", "Ice", "Bug", "Steel", "Fairy"],
    "Water": ["Fire", "Water", "Ice", "Steel"],
    "Grass": ["Water", "Electric", "Grass", "Ground"],
    "Electric": ["Electric", "Flying", "Steel"],
    "Ice": ["Ice"],
    "Fighting": ["Bug", "Rock", "Dark"],
    "Poison": ["Grass", "Fighting", "Poison", "Bug", "Fairy"],
    "Ground": ["Poison", "Rock"],
    "Flying": ["Grass", "Fighting", "Bug"],
    "Psychic": ["Fighting", "Psychic"],
    "Bug": ["Grass", "Fighting", "Ground"],
    "Rock": ["Normal", "Fire", "Poison", "Flying"],
    "Ghost": ["Poison", "Bug"],
    "Dragon": ["Fire", "Water", "Electric", "Grass"],
    "Dark": ["Ghost", "Dark", "Psychic"],
    "Steel": ["Normal", "Grass", "Ice", "Flying", "Psychic", "Bug", "Rock", "Dragon", "Steel", "Fairy"],
    "Fairy": ["Fighting", "Bug", "Dark"],
}


def type_checker(pkmn_type, items):
    weaknesses = []
    resistances = []
    for t in pkmn_type.split('/'):
        weaknesses.extend(type_effectiveness.get(t, []))
        resistances.extend(type_resistances.get(t, []))
    effective_types = [w for w in weaknesses if w not in resistances]
    if effective_types:
        effective_pokemon = [item for item in items if any(
            t in item['Type'].split('/') for t in effective_types)]
        if effective_pokemon:
            random_effective_pokemon = random.choice(effective_pokemon)
            return f"Weak to Pokémon like {random_effective_pokemon['Name']} ({random_effective_pokemon['Type']})"
    return "No specific weaknesses found."


def compare_stats(guessed_pkmn, randomized_pkmn):
    stats = ['Pokedex #', 'HP', 'Attack',
             'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
    comparison = []
    for stat in stats:
        if guessed_pkmn[stat] < randomized_pkmn[stat]:
            comparison.append(f"{stat}: ↑ ({guessed_pkmn[stat]})")
        elif guessed_pkmn[stat] > randomized_pkmn[stat]:
            comparison.append(f"{stat}: ↓ ({guessed_pkmn[stat]})")
        else:
            comparison.append(f"{stat}: = ({guessed_pkmn[stat]})")
    return ", ".join(comparison)


def pkmn_grabber(pkmn_guess, randomized_pkmn, items, gen_info, mega_items, guessed_pokemon):
    if (randomized_pkmn['Name'].lower() == "nidoran-m" and pkmn_guess.lower() in ["nidoran-m", "nidoran♂"]) or \
       (randomized_pkmn['Name'].lower() == "nidoran-f" and pkmn_guess.lower() in ["nidoran-f", "nidoran♀"]):
        slow_print(f"Correct! The Pokémon was {randomized_pkmn['Name']}.\n")
        slow_print(f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
        return True

    guessed_pkmn = find_item_by_name(items, pkmn_guess)

    # Check if the guessed Pokémon exists in the current generation
    if guessed_pkmn:
        if guessed_pkmn['Name'].lower() == randomized_pkmn['Name'].lower():
            slow_print(
                f"Correct! The Pokémon was {randomized_pkmn['Name']}.\n")
            slow_print(
                f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
            return True
        else:
            slow_print(
                f"Comparison with {guessed_pkmn['Name']}: {compare_stats(guessed_pkmn, randomized_pkmn)}")
            return False
    else:
        # Check for a mega version if in list6.json or listmega.json
        mega_version = find_mega_version(pkmn_guess, mega_items)
        if mega_version:
            slow_print(f"Did you mean: Mega {pkmn_guess.capitalize()}?")
            return None

        # Check if the guessed Pokémon exists in any generation
        all_items = load_all_items()
        guessed_pkmn_all_gens = find_item_by_name(all_items, pkmn_guess)

        if guessed_pkmn_all_gens:
            if gen_info.strip() == "Mega":
                slow_print("This Pokémon does not have a Mega-Evolution!")
            else:
                slow_print("This Pokémon is not in this generation!")
        else:
            similar_pokemon = find_similar_pokemon(
                pkmn_guess, items, guessed_pokemon)
            if similar_pokemon:
                slow_print(f"Did you mean: {', '.join(similar_pokemon)}?")
            else:
                slow_print("This is not a Pokémon!")

        return None


def find_similar_pokemon(pkmn_guess, items, guessed_pokemon):
    all_names = [item['Name'] for item in items]
    close_matches = get_close_matches(pkmn_guess, all_names, n=5, cutoff=0.6)

    # Collect all variations that match the base name
    variations = []
    base_name = pkmn_guess.split('-')[0].capitalize()
    for name in all_names:
        if name.lower().startswith(base_name.lower()) and name.lower() not in guessed_pokemon:
            variations.append(name)

    # Combine and deduplicate close matches and variations, excluding already guessed names
    suggestions = set(close_matches + variations) - set(guessed_pokemon.keys())
    return list(suggestions)


def generatePkmn(items):
    return random.choice(items)


def form_checker(pkmn):
    return pkmn.get('Forms', 'None').lower() != 'none'


def gender_checker(pkmn):
    if (pkmn.get('Gender Var.').lower() != 'yes'):
        return False
    return True


def shiny_chance(randomized_pkmn):
    if random.randint(1, 25) == 1:
        stat_to_reveal = random.choice(
            ['Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'])
        slow_print(
            f"✨WOAH! YOUR GUESSED POKEMON WAS SHINY! ✨ The Mystery Pokémon's {stat_to_reveal} stat is {randomized_pkmn[stat_to_reveal]}!\n")


def user_input(items, gen_info, mega_items=None, max_guesses=20, hints_allowed=True):
    randomized_pkmn = generatePkmn(items)
    incorrect_guesses = 0
    guessed_pokemon = {}  # Dictionary to track guessed Pokémon

    while True:
        pkmn_guess = input(
            f"\nWhat {gen_info}Pokémon am I thinking of?\n").strip().lower()

        # Check if the guess has already been made
        if pkmn_guess in guessed_pokemon:
            slow_print(
                f"You have already guessed {guessed_pokemon[pkmn_guess]['Name']}. Try a different one!\n")
            continue

        # Find the guessed Pokémon in the current items list
        current_guess = find_item_by_name(items, pkmn_guess)
        if current_guess:
            guessed_pokemon[pkmn_guess] = current_guess

        shiny_chance(randomized_pkmn)  # Check for shiny chance each guess

        result = pkmn_grabber(pkmn_guess, randomized_pkmn,
                              items, gen_info, mega_items, guessed_pokemon)

        if result is None:
            continue  # Do not count incorrect guess if Pokémon is not found

        if result:
            break

        incorrect_guesses += 1

        if hints_allowed and incorrect_guesses in {5, 8, 11, 14}:
            while True:
                hint = input(
                    "Would you like a hint? (yes/no)\n").strip().lower()
                if hint == 'yes':
                    if incorrect_guesses == 5:
                        form_hint = form_checker(randomized_pkmn)
                        gender_hint = gender_checker(randomized_pkmn)

                        if form_hint and gender_hint:
                            slow_print(
                                f"Hint: This Pokémon has forms: {randomized_pkmn['Forms']} and gender differences")
                        elif form_hint:
                            slow_print(
                                f"Hint: This Pokémon has forms: {randomized_pkmn['Forms']}\n")
                        elif gender_hint:
                            slow_print(
                                "Hint: This Pokémon has gender differences")
                        else:
                            slow_print(
                                "This Pokémon does not have any alternate forms or variants\n")
                    elif incorrect_guesses == 8:
                        weakness_hint = type_checker(
                            randomized_pkmn['Type'], items)
                        slow_print(f"Hint: {weakness_hint}\n")
                    elif incorrect_guesses == 11:
                        slow_print(
                            f"Hint: This Pokémon has the ability(s): {randomized_pkmn.get('Abilities', 'Unknown')}\n")
                    elif incorrect_guesses == 14:
                        slow_print(
                            f"Hint: The type of the Pokémon is {randomized_pkmn['Type']}\n")
                    break
                elif hint == 'no':
                    break

        if incorrect_guesses >= max_guesses:
            slow_print("You ran out of guesses. Sorry!")
            slow_print(f"The Pokémon was {randomized_pkmn['Name']}.")
            slow_print(
                f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
            break

    slow_print("Thanks for playing!\n\n\n")


def main():
    while True:
        choice = input(
            "Enter a number between 1 and 9, 'all', 'random', or 'mega' to select the Pokémon list: ").strip().lower()
        if choice.isdigit() and 1 <= int(choice) <= 9:
            items = load_items(f'list{choice}.json')
            gen_info = f"Gen {choice} "
            max_guesses = 20
            hints_allowed = True
            mega_items = load_mega_items()
            break
        elif choice == 'all':
            items = load_all_items()
            gen_info = ""
            max_guesses = 20
            hints_allowed = True
            mega_items = load_mega_items()
            break
        elif choice == 'random':
            rand_choice = random.randint(1, 9)
            items = load_items(f'list{rand_choice}.json')
            gen_info = f"Gen {rand_choice} "
            max_guesses = 20
            hints_allowed = True
            mega_items = load_mega_items()
            break
        elif choice == 'mega':
            items = load_items('listmega.json')
            gen_info = "Mega "
            max_guesses = 10
            hints_allowed = False
            mega_items = load_mega_items()
            break
        else:
            slow_print(
                "Invalid input. Please enter a number between 1 and 9, 'all', 'random', or 'mega'.\n")

    if gen_info:
        slow_print(f"Welcome to the Pokémon guessing game for {gen_info}!\n")
    else:
        slow_print("Welcome to the Pokémon guessing game!\n")
    user_input(items, gen_info, mega_items, max_guesses, hints_allowed)


if __name__ == "__main__":
    main()

# import time
# import sys
# import random
# import json
# import os
# from difflib import get_close_matches


# def load_items(file_path):
#     with open(file_path, 'r') as file:
#         return json.load(file)


# def load_all_items():
#     items = []
#     for i in range(1, 10):
#         file_path = f'list{i}.json'
#         if os.path.exists(file_path):
#             items.extend(load_items(file_path))
#     return items


# def find_item_by_name(items, item_name):
#     special_cases = {
#         "nidoran-m": "Nidoran-m",
#         "nidoran-f": "Nidoran-f"
#     }
#     item_name = special_cases.get(item_name.lower(), item_name)
#     for item in items:
#         if item['Name'].lower() == item_name.lower():
#             return item
#     return None


# def randomnumber(min_val, max_val):
#     return random.randint(min_val, max_val)


# def slow_print(text, delay=0.0411):
#     for char in text:
#         sys.stdout.write(char)
#         sys.stdout.flush()
#         time.sleep(delay)
#     print()


# def format_pokemon_details(pokemon):
#     return (
#         f"Name: {pokemon['Name']}\n"
#         f"Pokedex #: {pokemon['Pokedex #']}\n"
#         f"Type: {pokemon['Type']}\n"
#         f"Abilities: {pokemon.get('Abilities', 'Unknown')}\n"
#         f"HP: {pokemon['HP']}\n"
#         f"Attack: {pokemon['Attack']}\n"
#         f"Defense: {pokemon['Defense']}\n"
#         f"Sp. Atk: {pokemon['Sp. Atk']}\n"
#         f"Sp. Def: {pokemon['Sp. Def']}\n"
#         f"Speed: {pokemon['Speed']}\n"
#     )


# type_effectiveness = {
#     "Fire": ["Water", "Rock", "Ground"],
#     "Water": ["Electric", "Grass"],
#     "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
#     "Electric": ["Ground"],
#     "Ice": ["Fire", "Fighting", "Rock", "Steel"],
#     "Fighting": ["Flying", "Psychic", "Fairy"],
#     "Poison": ["Ground", "Psychic"],
#     "Ground": ["Water", "Ice", "Grass"],
#     "Flying": ["Electric", "Ice", "Rock"],
#     "Psychic": ["Bug", "Ghost", "Dark"],
#     "Bug": ["Fire", "Flying", "Rock"],
#     "Rock": ["Water", "Grass", "Fighting", "Ground", "Steel"],
#     "Ghost": ["Ghost", "Dark"],
#     "Dragon": ["Ice", "Dragon", "Fairy"],
#     "Dark": ["Fighting", "Bug", "Fairy"],
#     "Steel": ["Fire", "Fighting", "Ground"],
#     "Fairy": ["Poison", "Steel"],
# }

# type_resistances = {
#     "Fire": ["Fire", "Grass", "Ice", "Bug", "Steel", "Fairy"],
#     "Water": ["Fire", "Water", "Ice", "Steel"],
#     "Grass": ["Water", "Electric", "Grass", "Ground"],
#     "Electric": ["Electric", "Flying", "Steel"],
#     "Ice": ["Ice"],
#     "Fighting": ["Bug", "Rock", "Dark"],
#     "Poison": ["Grass", "Fighting", "Poison", "Bug", "Fairy"],
#     "Ground": ["Poison", "Rock"],
#     "Flying": ["Grass", "Fighting", "Bug"],
#     "Psychic": ["Fighting", "Psychic"],
#     "Bug": ["Grass", "Fighting", "Ground"],
#     "Rock": ["Normal", "Fire", "Poison", "Flying"],
#     "Ghost": ["Poison", "Bug"],
#     "Dragon": ["Fire", "Water", "Electric", "Grass"],
#     "Dark": ["Ghost", "Dark", "Psychic"],
#     "Steel": ["Normal", "Grass", "Ice", "Flying", "Psychic", "Bug", "Rock", "Dragon", "Steel", "Fairy"],
#     "Fairy": ["Fighting", "Bug", "Dark"],
# }


# def type_checker(pkmn_type, items):
#     weaknesses = []
#     resistances = []
#     for t in pkmn_type.split('/'):
#         weaknesses.extend(type_effectiveness.get(t, []))
#         resistances.extend(type_resistances.get(t, []))
#     effective_types = [w for w in weaknesses if w not in resistances]
#     if effective_types:
#         effective_pokemon = [item for item in items if any(
#             t in item['Type'].split('/') for t in effective_types)]
#         if effective_pokemon:
#             random_effective_pokemon = random.choice(effective_pokemon)
#             return f"Weak to Pokémon like {random_effective_pokemon['Name']} ({random_effective_pokemon['Type']})"
#     return "No specific weaknesses found."


# def compare_stats(guessed_pkmn, randomized_pkmn):
#     stats = ['Pokedex #', 'HP', 'Attack',
#              'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
#     comparison = []
#     for stat in stats:
#         if guessed_pkmn[stat] < randomized_pkmn[stat]:
#             comparison.append(f"{stat}: ↑ ({guessed_pkmn[stat]})")
#         elif guessed_pkmn[stat] > randomized_pkmn[stat]:
#             comparison.append(f"{stat}: ↓ ({guessed_pkmn[stat]})")
#         else:
#             comparison.append(f"{stat}: = ({guessed_pkmn[stat]})")
#     return ", ".join(comparison)


# def pkmn_grabber(pkmn_guess, randomized_pkmn, items, gen_info):
#     if (randomized_pkmn['Name'].lower() == "nidoran-m" and pkmn_guess.lower() in ["nidoran-m", "nidoran♂"]) or \
#        (randomized_pkmn['Name'].lower() == "nidoran-f" and pkmn_guess.lower() in ["nidoran-f", "nidoran♀"]):
#         slow_print(f"Correct! The Pokémon was {randomized_pkmn['Name']}.\n")
#         slow_print(f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
#         return True

#     guessed_pkmn = find_item_by_name(items, pkmn_guess)

#     # Check if the guessed Pokémon exists in the current generation
#     if guessed_pkmn:
#         if guessed_pkmn['Name'].lower() == randomized_pkmn['Name'].lower():
#             slow_print(
#                 f"Correct! The Pokémon was {randomized_pkmn['Name']}.\n")
#             slow_print(
#                 f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
#             return True
#         else:
#             slow_print(
#                 f"Comparison with {guessed_pkmn['Name']}: {compare_stats(guessed_pkmn, randomized_pkmn)}")
#             return False
#     else:
#         # Check if the guessed Pokémon exists in any generation
#         all_items = load_all_items()
#         guessed_pkmn_all_gens = find_item_by_name(all_items, pkmn_guess)

#         if guessed_pkmn_all_gens:
#             slow_print("This Pokémon is not in this generation!")
#         else:
#             similar_pokemon = find_similar_pokemon(pkmn_guess, items)
#             if similar_pokemon:
#                 slow_print(f"Did you mean: {', '.join(similar_pokemon)}?")
#             else:
#                 slow_print("This is not a Pokémon!")

#         return None


# def find_similar_pokemon(pkmn_guess, items):
#     all_names = [item['Name'] for item in items]
#     close_matches = get_close_matches(pkmn_guess, all_names, n=3, cutoff=0.6)
#     return close_matches


# def generatePkmn(items):
#     return random.choice(items)


# def form_checker(pkmn):
#     return pkmn.get('Forms', 'None').lower() != 'none'


# def shiny_chance(randomized_pkmn):
#     if random.randint(1, 25) == 1:
#         stat_to_reveal = random.choice(
#             ['Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'])
#         slow_print(
#             f"✨WOAH! YOUR GUESSED POKEMON WAS SHINY! ✨ The Mystery Pokémon's {stat_to_reveal} stat is {randomized_pkmn[stat_to_reveal]}!\n")


# def user_input(items, gen_info):
#     randomized_pkmn = generatePkmn(items)
#     incorrect_guesses = 0
#     guessed_pokemon = {}  # Dictionary to track guessed Pokémon

#     while True:
#         pkmn_guess = input(
#             f"\nWhat {gen_info}Pokémon am I thinking of?\n").strip().lower()

#         # Check if the guess has already been made
#         if pkmn_guess in guessed_pokemon:
#             slow_print(
#                 f"You have already guessed {guessed_pokemon[pkmn_guess]['Name']}. Try a different one!\n")
#             continue

#         # Find the guessed Pokémon in the current items list
#         current_guess = find_item_by_name(items, pkmn_guess)
#         if current_guess:
#             guessed_pokemon[pkmn_guess] = current_guess

#         shiny_chance(randomized_pkmn)  # Check for shiny chance each guess

#         result = pkmn_grabber(pkmn_guess, randomized_pkmn, items, gen_info)

#         if result is None:
#             continue  # Do not count incorrect guess if Pokémon is not found

#         if result:
#             break

#         incorrect_guesses += 1

#         if incorrect_guesses in {5, 8, 11, 14}:
#             while True:
#                 hint = input(
#                     "Would you like a hint? (yes/no)\n").strip().lower()
#                 if hint == 'yes':
#                     if incorrect_guesses == 5:
#                         if form_checker(randomized_pkmn):
#                             slow_print(
#                                 f"Hint: This Pokémon has forms: {randomized_pkmn['Forms']}\n")
#                         else:
#                             slow_print(
#                                 "This Pokémon does not have any alternate forms\n")
#                     elif incorrect_guesses == 8:
#                         weakness_hint = type_checker(
#                             randomized_pkmn['Type'], items)
#                         slow_print(f"Hint: {weakness_hint}\n")
#                     elif incorrect_guesses == 11:
#                         slow_print(
#                             f"Hint: This Pokémon has the ability(s): {randomized_pkmn.get('Abilities', 'Unknown')}\n")
#                     elif incorrect_guesses == 14:
#                         slow_print(
#                             f"Hint: The type of the Pokémon is {randomized_pkmn['Type']}\n")
#                     break
#                 elif hint == 'no':
#                     break

#         if incorrect_guesses >= 20:
#             slow_print("You ran out of guesses. Sorry!")
#             slow_print(f"The Pokémon was {randomized_pkmn['Name']}.")
#             slow_print(
#                 f"Details:\n{format_pokemon_details(randomized_pkmn)}\n")
#             break

#     slow_print("Thanks for playing!\n\n\n")


# def main():
#     while True:
#         choice = input(
#             "Enter a number between 1 and 9, 'all', or 'random' to select the Pokémon list: ").strip().lower()
#         if choice.isdigit() and 1 <= int(choice) <= 9:
#             items = load_items(f'list{choice}.json')
#             gen_info = f"Gen {choice} "
#             break
#         elif choice == 'all':
#             items = load_all_items()
#             gen_info = ""
#             break
#         elif choice == 'random':
#             rand_choice = random.randint(1, 9)
#             items = load_items(f'list{rand_choice}.json')
#             gen_info = f"Gen {rand_choice} "
#             break
#         else:
#             slow_print(
#                 "Invalid input. Please enter a number between 1 and 9, 'all', or 'random'.\n")

#     if gen_info:
#         slow_print(f"Welcome to the Pokémon guessing game for {gen_info}!\n")
#     else:
#         slow_print("Welcome to the Pokémon guessing game!\n")
#     user_input(items, gen_info)


# if __name__ == "__main__":
#     main()
