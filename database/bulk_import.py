#!/usr/bin/env python3
"""
Bulk Sumo Data Import
Downloads and imports complete sumo database from 1958-present
Target: ~50,000 bouts across ~400 tournaments
"""

import sqlite3
import requests
import time
import json
from datetime import datetime, date
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SumoBulkImporter:
    def __init__(self, db_path="database/sumo.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.session = requests.Session()
        
    def init_database(self):
        """Initialize database with schema"""
        with open("database/setup.sql", 'r') as f:
            schema = f.read()
        self.conn.executescript(schema)
        logger.info("Database initialized")
        
    def fetch_all_tournaments(self):
        """Download every tournament from 1958-present"""
        tournaments = []
        
        # Generate all tournament dates since 1958
        for year in range(1958, datetime.now().year + 1):
            for month in [1, 3, 5, 7, 9, 11]:
                # Skip future tournaments
                if date(year, month, 1) > date.today():
                    continue
                    
                tournament_id = f"{year}{month:02d}"
                try:
                    logger.info(f"Fetching tournament {tournament_id}")
                    
                    # Fetch tournament metadata
                    url = f"https://www.sumo-api.com/api/basho/{tournament_id}"
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        tournament = {
                            'id': tournament_id,
                            'year': year,
                            'month': month,
                            'location': self._get_location(month),
                            'start_date': data.get('start_date'),
                            'end_date': data.get('end_date')
                        }
                        tournaments.append(tournament)
                        
                        # Fetch all data for this tournament
                        self.fetch_tournament_complete(tournament_id)
                        
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Failed to fetch {tournament_id}: {e}")
                    
        return tournaments
    
    def fetch_tournament_complete(self, tournament_id):
        """Fetch complete data for one tournament: banzuke + all 15 days of bouts"""
        
        # Fetch banzuke (rankings)
        try:
            url = f"https://www.sumo-api.com/api/basho/{tournament_id}/banzuke"
            banzuke_data = self.session.get(url).json()
            self.import_banzuke(tournament_id, banzuke_data)
        except Exception as e:
            logger.error(f"Failed banzuke for {tournament_id}: {e}")
            
        # Fetch all daily results
        all_bouts = []
        for day in range(1, 16):
            try:
                url = f"https://www.sumo-api.com/api/basho/{tournament_id}/torikumi/{day}"
                day_data = self.session.get(url).json()
                
                if 'torikumi' in day_data:
                    for bout in day_data['torikumi']:
                        bout['tournament_id'] = tournament_id
                        bout['day'] = day
                        all_bouts.append(bout)
                        
                time.sleep(0.5)  # Rate limiting between days
                
            except Exception as e:
                logger.warning(f"Failed day {day} for {tournament_id}: {e}")
                
        self.import_bouts(all_bouts)
        logger.info(f"Imported {len(all_bouts)} bouts for {tournament_id}")
        
    def import_wrestlers(self, wrestlers_data):
        """Import wrestler profiles in bulk"""
        wrestlers = []
        
        for wrestler in wrestlers_data:
            wrestlers.append((
                wrestler.get('id'),
                wrestler.get('shikona', ''),
                wrestler.get('real_name', ''),
                wrestler.get('birth_date'),
                wrestler.get('debut_date'),
                wrestler.get('retirement_date'),
                wrestler.get('height'),
                wrestler.get('weight'),
                wrestler.get('shusshin', ''),
                wrestler.get('heya', ''),
                self._is_foreign_born(wrestler.get('shusshin', ''))
            ))
            
        self.conn.executemany("""
            INSERT OR REPLACE INTO wrestlers 
            (id, shikona, real_name, birth_date, debut_date, retirement_date, 
             height_cm, weight_kg, shusshin, heya, foreign_born)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, wrestlers)
        
        logger.info(f"Imported {len(wrestlers)} wrestlers")
        
    def import_banzuke(self, tournament_id, banzuke_data):
        """Import rankings for one tournament"""
        rankings = []
        
        for division, wrestlers in banzuke_data.items():
            if isinstance(wrestlers, list):
                for wrestler in wrestlers:
                    rankings.append((
                        tournament_id,
                        wrestler.get('id'),
                        division,
                        wrestler.get('rank', ''),
                        self._parse_rank_number(wrestler.get('rank', '')),
                        wrestler.get('side', 'east')  # east/west
                    ))
                    
        self.conn.executemany("""
            INSERT OR REPLACE INTO banzuke 
            (tournament_id, wrestler_id, division, rank, rank_number, east_west)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rankings)
        
    def import_bouts(self, bouts_data):
        """Import bout results in bulk"""
        bouts = []
        
        for i, bout in enumerate(bouts_data):
            bouts.append((
                None,  # Auto-increment ID
                bout['tournament_id'],
                bout['day'],
                bout.get('division', 'makuuchi'),
                bout.get('east', {}).get('id'),
                bout.get('west', {}).get('id'),
                bout.get('winner_id'),
                bout.get('kimarite', ''),
                bout.get('match_time')
            ))
            
        self.conn.executemany("""
            INSERT INTO bouts 
            (id, tournament_id, day, division, east_wrestler_id, west_wrestler_id, 
             winner_id, kimarite, match_time_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, bouts)
        
    def fetch_all_wrestlers(self):
        """Download complete wrestler database"""
        wrestlers = []
        
        # Get all divisions
        divisions = ['makuuchi', 'juryo', 'makushita', 'sandanme', 'jonidan', 'jonokuchi']
        
        for division in divisions:
            try:
                url = f"https://www.sumo-api.com/api/rikishi"
                params = {'division': division, 'limit': 1000}
                
                response = self.session.get(url, params=params)
                data = response.json()
                
                if 'records' in data:
                    wrestlers.extend(data['records'])
                    logger.info(f"Fetched {len(data['records'])} {division} wrestlers")
                    
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to fetch {division} wrestlers: {e}")
                
        self.import_wrestlers(wrestlers)
        return wrestlers
        
    def create_bulk_stats(self):
        """Generate aggregate statistics tables"""
        
        # Calculate wrestler tournament records
        self.conn.execute("""
            INSERT OR REPLACE INTO wrestler_tournaments
            SELECT 
                COALESCE(b_east.wrestler_id, b_west.wrestler_id) as wrestler_id,
                tournament_id,
                division,
                '' as rank,  -- Fill from banzuke
                COALESCE(wins, 0) as wins,
                COALESCE(losses, 0) as losses,
                0 as absences  -- Calculate separately
            FROM (
                SELECT 
                    east_wrestler_id as wrestler_id,
                    tournament_id,
                    division,
                    SUM(CASE WHEN winner_id = east_wrestler_id THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN winner_id != east_wrestler_id THEN 1 ELSE 0 END) as losses
                FROM bouts 
                GROUP BY east_wrestler_id, tournament_id, division
            ) b_east
            FULL OUTER JOIN (
                SELECT 
                    west_wrestler_id as wrestler_id,
                    tournament_id,
                    division,
                    SUM(CASE WHEN winner_id = west_wrestler_id THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN winner_id != west_wrestler_id THEN 1 ELSE 0 END) as losses
                FROM bouts 
                GROUP BY west_wrestler_id, tournament_id, division
            ) b_west ON b_east.wrestler_id = b_west.wrestler_id 
                    AND b_east.tournament_id = b_west.tournament_id
        """)
        
        self.conn.commit()
        logger.info("Generated wrestler tournament statistics")
        
    def _get_location(self, month):
        """Map tournament month to location"""
        locations = {
            1: 'Tokyo', 3: 'Osaka', 5: 'Tokyo', 
            7: 'Nagoya', 9: 'Tokyo', 11: 'Fukuoka'
        }
        return locations.get(month, 'Tokyo')
        
    def _is_foreign_born(self, shusshin):
        """Detect foreign-born wrestlers by birthplace"""
        if not shusshin:
            return False
        japanese_indicators = [
            'Tokyo', 'Osaka', 'Kyoto', 'Hokkaido', 'Fukuoka', 'Aichi', 'Kanagawa',
            'Prefecture', '県', '都', '府', '道'
        ]
        return not any(indicator in shusshin for indicator in japanese_indicators)
        
    def _parse_rank_number(self, rank_str):
        """Extract numeric rank for ordering"""
        if not rank_str:
            return 999
        # Logic to convert Y1, O1, S1, K1, M1, J1 etc to numbers
        # Simplified for now
        return 0
        
    def run_complete_import(self):
        """Execute complete data import"""
        logger.info("Starting complete sumo database import")
        
        # Initialize
        self.init_database()
        
        # Import wrestlers first
        self.fetch_all_wrestlers()
        
        # Import all tournaments (this will take hours)
        tournaments = self.fetch_all_tournaments()
        
        # Generate statistics
        self.create_bulk_stats()
        
        # Final summary
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bouts")
        bout_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM wrestlers")
        wrestler_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tournaments")
        tournament_count = cursor.fetchone()[0]
        
        logger.info(f"Import complete: {bout_count} bouts, {wrestler_count} wrestlers, {tournament_count} tournaments")
        
        self.conn.close()

if __name__ == "__main__":
    importer = SumoBulkImporter()
    importer.run_complete_import()