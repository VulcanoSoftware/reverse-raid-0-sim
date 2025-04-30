import os
import shutil
import yaml
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

def maak_standaard_configuratie():
    """Maak een standaard configuratiebestand aan."""
    standaard_config = {
        'aantal_mappen': 5,          # Standaard aantal mappen
        'source_paths': [''] * 5,    # 5 lege bronpaden als standaard
        'destination_path': '',      # Leeg doelpad
        'minimum_leeftijd_uren': 12, # Standaard minimum leeftijd in uren
        'uitvoer_interval_minuten': 10,  # Standaard interval in minuten
        'console_wissen_interval_uren': 6,  # Standaard console wissen interval in uren
        'discord_webhook_url': ''    # Discord webhook URL
    }
    return standaard_config

def laad_configuratie():
    """Laad de configuratie uit het YAML-bestand of maak een nieuw bestand aan als het niet bestaat."""
    config_bestand = 'reverseraid.yml'
    
    # Controleer of het configuratiebestand bestaat
    if not os.path.exists(config_bestand):
        print(f"Het configuratiebestand '{config_bestand}' bestaat niet. Een nieuw bestand wordt aangemaakt.")
        config = maak_standaard_configuratie()
        
        try:
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            print(f"Nieuw configuratiebestand '{config_bestand}' succesvol aangemaakt.")
        except Exception as e:
            print(f"Fout bij het aanmaken van het configuratiebestand: {e}")
            sys.exit(1)
            
        return config
    
    # Laad de configuratie
    try:
        with open(config_bestand, 'r') as f:
            config = yaml.safe_load(f)
        
        # Controleer of de vereiste configuratievelden aanwezig zijn
        if 'source_paths' not in config or 'destination_path' not in config:
            print("Fout: Het configuratiebestand mist verplichte velden (source_paths of destination_path).")
            print("Het bestand wordt hersteld naar de standaardwaarden.")
            
            config = maak_standaard_configuratie()
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        
        # Voeg aantal_mappen toe als het ontbreekt
        if 'aantal_mappen' not in config:
            config['aantal_mappen'] = len(config['source_paths'])
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        # Voeg minimum leeftijd toe als deze ontbreekt
        if 'minimum_leeftijd_uren' not in config:
            config['minimum_leeftijd_uren'] = 12  # Standaard 12 uur
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        # Voeg uitvoer interval toe als deze ontbreekt
        if 'uitvoer_interval_minuten' not in config:
            config['uitvoer_interval_minuten'] = 10  # Standaard 10 minuten
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        # Voeg console wissen interval toe als deze ontbreekt
        if 'console_wissen_interval_uren' not in config:
            config['console_wissen_interval_uren'] = 6  # Standaard 6 uur
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        # Voeg Discord webhook URL toe als deze ontbreekt
        if 'discord_webhook_url' not in config:
            config['discord_webhook_url'] = ''  # Standaard lege string
            with open(config_bestand, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        return config
    except Exception as e:
        print(f"Fout bij het laden van de configuratie: {e}")
        sys.exit(1)

def vraag_en_update_aantal_mappen(config):
    """Vraag hoeveel mappen de gebruiker wil configureren."""
    huidige_aantal = config.get('aantal_mappen', len(config['source_paths']))
    
    try:
        nieuw_aantal = input(f"Hoeveel bronmappen wilt u configureren? [{huidige_aantal}]: ")
        if nieuw_aantal.strip():
            nieuw_aantal = int(nieuw_aantal)
            if nieuw_aantal < 1:
                print("Er moet minimaal 1 bronmap zijn. Het aantal wordt ingesteld op 1.")
                nieuw_aantal = 1
            
            if nieuw_aantal != huidige_aantal:
                config['aantal_mappen'] = nieuw_aantal
                
                # Pas het aantal bronpaden aan
                if len(config['source_paths']) > nieuw_aantal:
                    # Verwijder overtollige paden
                    config['source_paths'] = config['source_paths'][:nieuw_aantal]
                else:
                    # Voeg extra lege paden toe
                    config['source_paths'].extend([''] * (nieuw_aantal - len(config['source_paths'])))
                
                # Sla de gewijzigde configuratie op
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print(f"Aantal bronmappen bijgewerkt naar {nieuw_aantal}.")
        else:
            # Als er geen invoer is, zorg ervoor dat het aantal_mappen veld overeenkomt met het aantal paden
            if huidige_aantal != len(config['source_paths']):
                config['aantal_mappen'] = len(config['source_paths'])
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
    except ValueError:
        print("Ongeldige invoer. Het aantal blijft ongewijzigd.")
    except Exception as e:
        print(f"Fout bij het bijwerken van het aantal mappen: {e}")
    
    return config

def vraag_en_update_leeftijd(config):
    """Vraag de minimale leeftijd van bestanden die verplaatst moeten worden."""
    huidige_leeftijd = config.get('minimum_leeftijd_uren', 12)
    
    try:
        nieuwe_leeftijd = input(f"Minimale leeftijd van bestanden in uren? [{huidige_leeftijd}]: ")
        if nieuwe_leeftijd.strip():
            nieuwe_leeftijd = float(nieuwe_leeftijd)
            if nieuwe_leeftijd < 0:
                print("De leeftijd kan niet negatief zijn. De waarde wordt ingesteld op 0.")
                nieuwe_leeftijd = 0
            
            if nieuwe_leeftijd != huidige_leeftijd:
                config['minimum_leeftijd_uren'] = nieuwe_leeftijd
                
                # Sla de gewijzigde configuratie op
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print(f"Minimale leeftijd bijgewerkt naar {nieuwe_leeftijd} uur.")
    except ValueError:
        print("Ongeldige invoer. De leeftijd blijft ongewijzigd.")
    except Exception as e:
        print(f"Fout bij het bijwerken van de minimale leeftijd: {e}")
    
    return config

def vraag_en_update_interval(config):
    """Vraag het interval tussen uitvoeringen in minuten."""
    huidig_interval = config.get('uitvoer_interval_minuten', 10)
    
    try:
        nieuw_interval = input(f"Interval tussen uitvoeringen in minuten? [{huidig_interval}]: ")
        if nieuw_interval.strip():
            nieuw_interval = float(nieuw_interval)
            if nieuw_interval < 1:
                print("Het interval moet minimaal 1 minuut zijn. De waarde wordt ingesteld op 1.")
                nieuw_interval = 1
            
            if nieuw_interval != huidig_interval:
                config['uitvoer_interval_minuten'] = nieuw_interval
                
                # Sla de gewijzigde configuratie op
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print(f"Uitvoeringsinterval bijgewerkt naar {nieuw_interval} minuten.")
    except ValueError:
        print("Ongeldige invoer. Het interval blijft ongewijzigd.")
    except Exception as e:
        print(f"Fout bij het bijwerken van het interval: {e}")
    
    return config

def vraag_en_update_console_wissen_interval(config):
    """Vraag het interval voor het wissen van de console in uren."""
    huidig_interval = config.get('console_wissen_interval_uren', 6)
    
    try:
        nieuw_interval = input(f"Interval voor het wissen van de console in uren? [{huidig_interval}]: ")
        if nieuw_interval.strip():
            nieuw_interval = float(nieuw_interval)
            if nieuw_interval < 0:
                print("Het interval kan niet negatief zijn. De waarde wordt ingesteld op 0 (nooit wissen).")
                nieuw_interval = 0
            
            if nieuw_interval != huidig_interval:
                config['console_wissen_interval_uren'] = nieuw_interval
                
                # Sla de gewijzigde configuratie op
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print(f"Console wissen interval bijgewerkt naar {nieuw_interval} uur.")
    except ValueError:
        print("Ongeldige invoer. Het interval blijft ongewijzigd.")
    except Exception as e:
        print(f"Fout bij het bijwerken van het console wissen interval: {e}")
    
    return config

def vraag_en_update_discord_webhook(config):
    """Vraag de Discord webhook URL."""
    huidige_webhook = config.get('discord_webhook_url', '')
    verborgen_webhook = "********" if huidige_webhook else ""
    
    try:
        if huidige_webhook:
            nieuwe_webhook = input(f"Discord webhook URL? [{verborgen_webhook}] (Druk enter om te behouden of 'x' om te wissen): ")
            if nieuwe_webhook.lower() == 'x':
                config['discord_webhook_url'] = ''
                print("Discord webhook verwijderd.")
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            elif nieuwe_webhook.strip():
                config['discord_webhook_url'] = nieuwe_webhook
                print("Discord webhook bijgewerkt.")
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
        else:
            nieuwe_webhook = input("Discord webhook URL? (Laat leeg om over te slaan): ")
            if nieuwe_webhook.strip():
                config['discord_webhook_url'] = nieuwe_webhook
                print("Discord webhook ingesteld.")
                with open('reverseraid.yml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                # Test de webhook
                test_succes = verstuur_discord_bericht(nieuwe_webhook, "Test bericht van Reverse RAID 0 Simulator. De webhook is succesvol ingesteld!")
                if test_succes:
                    print("Testbericht succesvol verstuurd naar Discord.")
                else:
                    print("Waarschuwing: Kon geen testbericht versturen. Controleer de webhook URL.")
    except Exception as e:
        print(f"Fout bij het bijwerken van de Discord webhook: {e}")
    
    return config

def vraag_en_update_paden(config):
    """Vraag om ontbrekende paden en update het configuratiebestand."""
    gewijzigd = False
    
    # Controleer bronpaden
    for i in range(len(config['source_paths'])):
        if not config['source_paths'][i]:
            config['source_paths'][i] = input(f"Geef pad naar bronmap {i+1}: ")
            gewijzigd = True
    
    # Controleer doelpad
    if not config['destination_path']:
        config['destination_path'] = input("Geef pad naar doelmap: ")
        gewijzigd = True
    
    # Update het configuratiebestand als er wijzigingen zijn
    if gewijzigd:
        try:
            with open('reverseraid.yml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            print("Configuratie succesvol bijgewerkt.")
        except Exception as e:
            print(f"Fout bij het opslaan van de configuratie: {e}")
            sys.exit(1)
    
    return config

def valideer_paden(config):
    """Valideer of de opgegeven paden bestaan."""
    for i, pad in enumerate(config['source_paths']):
        if not os.path.isdir(pad):
            print(f"Waarschuwing: Bronmap {i+1} ({pad}) bestaat niet of is geen map.")
            return False
    
    if not os.path.isdir(config['destination_path']):
        print(f"Waarschuwing: Doelmap ({config['destination_path']}) bestaat niet of is geen map.")
        return False
    
    return True

def verstuur_discord_bericht(webhook_url, bericht):
    """Verstuur een bericht naar Discord via een webhook."""
    if not webhook_url:
        return False
    
    try:
        data = {
            "content": bericht
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        
        if response.status_code == 204:
            return True
        else:
            print(f"Fout bij versturen Discord bericht: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Fout bij versturen Discord bericht: {e}")
        return False

def logboek_bericht(config, bericht, console_output=True, belangrijk=True):
    """Verstuur een bericht naar het logboek (console en Discord).
    Param belangrijk: Alleen belangrijk=True berichten worden naar Discord gestuurd"""
    # Voeg tijdstempel toe
    tijdstempel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    volledig_bericht = f"[{tijdstempel}] {bericht}"
    
    # Output naar console
    if console_output:
        print(volledig_bericht)
    
    # Verstuur naar Discord als de webhook is geconfigureerd en het bericht belangrijk is
    discord_webhook_url = config.get('discord_webhook_url', '')
    if discord_webhook_url and belangrijk:
        verstuur_discord_bericht(discord_webhook_url, volledig_bericht)

def verplaats_bestanden(config):
    """Verplaats bestanden van bronmappen naar doelmap."""
    doelmap = config['destination_path']
    
    # Haal de minimale leeftijd uit de configuratie
    minimum_leeftijd = config.get('minimum_leeftijd_uren', 12)
    
    # Zorg ervoor dat de doelmap bestaat
    os.makedirs(doelmap, exist_ok=True)
    
    # Bereken de tijdsgrens (minimale leeftijd in uren geleden)
    tijdsgrens = time.time() - (minimum_leeftijd * 60 * 60)  # Uren naar seconden
    huidig_tijdstip = datetime.now()
    tijdsgrens_datetime = huidig_tijdstip - timedelta(hours=minimum_leeftijd)
    
    totaal_bestanden = 0
    totaal_verplaatst = 0
    totaal_overgeslagen_te_nieuw = 0
    
    logboek_bericht(config, f"Begin met verplaatsen van bestanden (alleen bestanden ouder dan {minimum_leeftijd} uur)...")
    
    # Loop door alle bronmappen
    for i, bronmap in enumerate(config['source_paths']):
        if not os.path.isdir(bronmap):
            logboek_bericht(config, f"Overslaan van bronmap {i+1}: Map bestaat niet of is geen map.", belangrijk=True)
            continue
        
        bestanden_in_map = 0
        verplaatst_in_map = 0
        
        # Loop door alle bestanden in de bronmap
        bestanden = [f for f in os.listdir(bronmap) if os.path.isfile(os.path.join(bronmap, f))]
        
        for bestand in bestanden:
            bron_pad = os.path.join(bronmap, bestand)
            doel_pad = os.path.join(doelmap, bestand)
            
            # Controleer de leeftijd van het bestand
            bestand_tijd = os.path.getmtime(bron_pad)
            bestand_leeftijd_uren = (time.time() - bestand_tijd) / 3600
            
            # Alleen verwerken als het bestand ouder is dan de minimale leeftijd
            if bestand_leeftijd_uren < minimum_leeftijd:
                logboek_bericht(config, f"  Overslaan: {bestand} is te nieuw (leeftijd: {bestand_leeftijd_uren:.1f} uur).", belangrijk=False)
                totaal_overgeslagen_te_nieuw += 1
                continue
                
            totaal_bestanden += 1
            bestanden_in_map += 1
            
            # Controleer of het bestand al bestaat in de doelmap
            if os.path.exists(doel_pad):
                logboek_bericht(config, f"  Overslaan: {bestand} bestaat al in de doelmap.", belangrijk=False)
                continue
            
            try:
                # Verplaats het bestand
                shutil.move(bron_pad, doel_pad)
                logboek_bericht(config, f"  Verplaatst: {bestand}", belangrijk=False)
                totaal_verplaatst += 1
                verplaatst_in_map += 1
            except Exception as e:
                logboek_bericht(config, f"  Fout bij verplaatsen van {bestand}: {e}", belangrijk=True)
        
        # Toon samenvatting per map alleen als er bestanden zijn verplaatst
        if bestanden_in_map > 0:
            logboek_bericht(config, f"Map {i+1}: {verplaatst_in_map} van {bestanden_in_map} bestanden verplaatst uit {bronmap}", belangrijk=(verplaatst_in_map > 0))
    
    # Alleen een resultaatbericht sturen als er daadwerkelijk bestanden zijn verplaatst
    if totaal_verplaatst > 0 or totaal_bestanden > 0:
        resultaat_bericht = f"Verplaatsing voltooid: {totaal_verplaatst} van {totaal_bestanden} bestanden verplaatst naar {doelmap}"
        logboek_bericht(config, resultaat_bericht, belangrijk=True)
    else:
        logboek_bericht(config, "Geen bestanden verplaatst in deze cyclus", belangrijk=False)

def wis_console():
    """Wis de console op basis van het besturingssysteem."""
    # Voor Windows
    if os.name == 'nt':
        os.system('cls')
    # Voor Mac en Linux
    else:
        os.system('clear')

def verwerk_bestanden():
    """Hoofdfunctie voor het verwerken van bestanden."""
    print("Reverse RAID 0 Simulator")
    print("========================\n")
    
    # Laad configuratie
    config = laad_configuratie()
    
    # Vraag hoeveel mappen de gebruiker wil configureren
    config = vraag_en_update_aantal_mappen(config)
    
    # Vraag de minimale leeftijd van bestanden
    config = vraag_en_update_leeftijd(config)
    
    # Vraag het interval tussen uitvoeringen
    config = vraag_en_update_interval(config)
    
    # Vraag het interval voor het wissen van de console
    config = vraag_en_update_console_wissen_interval(config)
    
    # Vraag de Discord webhook URL
    config = vraag_en_update_discord_webhook(config)
    
    # Vraag om ontbrekende paden
    config = vraag_en_update_paden(config)
    
    # Valideer paden zonder om bevestiging te vragen
    if not valideer_paden(config):
        print("Doorgaan ondanks waarschuwingen...")
    
    return config

def main():
    """Hoofdfunctie die in een lus draait en bestanden verwerkt volgens het geconfigureerde interval."""
    # Initiële configuratie
    config = verwerk_bestanden()
    
    # Haal het interval op
    interval_minuten = config.get('uitvoer_interval_minuten', 10)
    console_wissen_interval_uren = config.get('console_wissen_interval_uren', 6)
    discord_webhook_url = config.get('discord_webhook_url', '')
    
    discord_status = "ingeschakeld" if discord_webhook_url else "uitgeschakeld"
    logboek_bericht(config, f"Programma draait met een interval van {interval_minuten} minuten. Discord notificaties: {discord_status}.")
    if console_wissen_interval_uren > 0:
        logboek_bericht(config, f"De console wordt elke {console_wissen_interval_uren} uur gewist.", belangrijk=False)
    
    logboek_bericht(config, "Druk Ctrl+C om het programma te stoppen.\n", belangrijk=False)
    
    # Bijhouden wanneer de console voor het laatst is gewist
    laatste_console_wis = datetime.now()
    
    try:
        while True:
            # Controleer of de console moet worden gewist
            huidige_tijd = datetime.now()
            if console_wissen_interval_uren > 0 and (huidige_tijd - laatste_console_wis).total_seconds() >= (console_wissen_interval_uren * 3600):
                wis_console()
                laatste_console_wis = huidige_tijd
                logboek_bericht(config, "Console gewist", belangrijk=False)
                logboek_bericht(config, "Reverse RAID 0 Simulator", belangrijk=False)
            
            # Verplaats bestanden
            verplaats_bestanden(config)
            
            # Toon wanneer de volgende uitvoering is
            volgende_uitvoering = datetime.now() + timedelta(minutes=interval_minuten)
            logboek_bericht(config, f"Volgende run: {volgende_uitvoering.strftime('%H:%M:%S')}", belangrijk=False)
            
            # Wacht tot het tijd is voor de volgende uitvoering
            time.sleep(interval_minuten * 60)
            
            # Werk de configuratie bij voor het geval deze is gewijzigd
            config = laad_configuratie()
            interval_minuten = config.get('uitvoer_interval_minuten', 10)
            console_wissen_interval_uren = config.get('console_wissen_interval_uren', 6)
            
    except KeyboardInterrupt:
        logboek_bericht(config, "Programma gestopt door gebruiker.")
    except Exception as e:
        logboek_bericht(config, f"Fout tijdens uitvoering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 