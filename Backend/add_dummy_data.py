"""
Populate the database with dummy data for testing
"""
import json
import logging
import random
from datetime import datetime, timedelta
from database.connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_dummy_data():
    """Add dummy data to all tables for testing"""
    try:
        # Check if we already have users
        users_query = "SELECT id FROM users LIMIT 1;"
        existing_users = db.execute_query(users_query)
        
        # If no users exist, create some
        if not existing_users:
            logger.info("Creating dummy users...")
            create_dummy_users()
        
        # Get all user IDs
        users = db.execute_query("SELECT id FROM users;")
        user_ids = [user['id'] for user in users]
        
        if not user_ids:
            logger.error("No users found in the database.")
            return False
        
        # Add dummy wardrobe items
        add_dummy_wardrobe_items(user_ids)
        
        # Add dummy outfit history
        add_dummy_outfit_history(user_ids)
        
        # Add dummy favorite outfits
        add_dummy_favorite_outfits(user_ids)
        
        # Add dummy trip plans
        add_dummy_trip_plans(user_ids)
        
        logger.info("Dummy data added successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error adding dummy data: {e}")
        return False

def create_dummy_users():
    """Create dummy users"""
    users = [
        ('demo@styra.com', '$2b$12$dummy.hash.for.demo', 'Demo User'),
        ('john@example.com', '$2b$12$dummy.hash.for.john', 'John Smith'),
        ('alice@example.com', '$2b$12$dummy.hash.for.alice', 'Alice Johnson')
    ]
    
    for email, password_hash, name in users:
        insert_query = """
            INSERT INTO users (email, password_hash, name)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """
        db.execute_query(insert_query, (email, password_hash, name), fetch=False)
    
    logger.info(f"Added {len(users)} dummy users")

def add_dummy_wardrobe_items(user_ids):
    """Add dummy wardrobe items for users"""
    
    # Check if we already have enough wardrobe items
    items_count_query = "SELECT COUNT(*) as count FROM wardrobe_items;"
    items_count = db.execute_query(items_count_query)[0]['count']
    
    if items_count >= 20:
        logger.info(f"Already have {items_count} wardrobe items, skipping creation...")
        return
    
    wardrobe_items = [
        # Tops
        ('Blue Cotton T-Shirt', 'tops', 'Blue', 'summer', '/static/images/wardrobe/blue_tshirt.jpg', 0.92),
        ('White Button-Up Shirt', 'tops', 'White', 'all', '/static/images/wardrobe/white_shirt.jpg', 0.88),
        ('Black Polo Shirt', 'tops', 'Black', 'all', '/static/images/wardrobe/black_polo.jpg', 0.90),
        ('Red Flannel Shirt', 'tops', 'Red', 'fall', '/static/images/wardrobe/red_flannel.jpg', 0.85),
        ('Gray Sweater', 'tops', 'Gray', 'winter', '/static/images/wardrobe/gray_sweater.jpg', 0.89),
        
        # Bottoms
        ('Blue Denim Jeans', 'bottoms', 'Blue', 'all', '/static/images/wardrobe/blue_jeans.jpg', 0.95),
        ('Black Dress Pants', 'bottoms', 'Black', 'all', '/static/images/wardrobe/black_pants.jpg', 0.91),
        ('Khaki Chinos', 'bottoms', 'Beige', 'all', '/static/images/wardrobe/khaki_chinos.jpg', 0.87),
        ('Navy Shorts', 'bottoms', 'Navy', 'summer', '/static/images/wardrobe/navy_shorts.jpg', 0.88),
        ('Gray Sweatpants', 'bottoms', 'Gray', 'all', '/static/images/wardrobe/gray_sweatpants.jpg', 0.84),
        
        # Shoes
        ('Black Dress Shoes', 'shoes', 'Black', 'all', '/static/images/wardrobe/black_dress_shoes.jpg', 0.93),
        ('White Sneakers', 'shoes', 'White', 'all', '/static/images/wardrobe/white_sneakers.jpg', 0.92),
        ('Brown Leather Boots', 'shoes', 'Brown', 'fall', '/static/images/wardrobe/brown_boots.jpg', 0.90),
        ('Blue Running Shoes', 'shoes', 'Blue', 'all', '/static/images/wardrobe/blue_running_shoes.jpg', 0.91),
        ('Black Sandals', 'shoes', 'Black', 'summer', '/static/images/wardrobe/black_sandals.jpg', 0.85),
        
        # Outerwear
        ('Black Leather Jacket', 'outerwear', 'Black', 'fall', '/static/images/wardrobe/black_leather_jacket.jpg', 0.94),
        ('Navy Blazer', 'outerwear', 'Navy', 'all', '/static/images/wardrobe/navy_blazer.jpg', 0.92),
        ('Green Parka', 'outerwear', 'Green', 'winter', '/static/images/wardrobe/green_parka.jpg', 0.89),
        ('Gray Cardigan', 'outerwear', 'Gray', 'spring', '/static/images/wardrobe/gray_cardigan.jpg', 0.87),
        ('Blue Denim Jacket', 'outerwear', 'Blue', 'spring', '/static/images/wardrobe/denim_jacket.jpg', 0.90)
    ]
    
    for user_id in user_ids:
        # Add some random items for each user
        items_to_add = random.sample(wardrobe_items, min(15, len(wardrobe_items)))
        
        for name, category, color, season, image_path, confidence in items_to_add:
            # Add some randomness to avoid exact duplicates
            modified_name = f"{name} ({random.randint(1, 999)})"
            
            insert_query = """
                INSERT INTO wardrobe_items 
                (user_id, name, category, color, season, image_path, confidence, analysis_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """
            
            db.execute_query(
                insert_query, 
                (user_id, modified_name, category, color, season, image_path, confidence, 'free_ai_analysis'),
                fetch=False
            )
    
    # Check how many items we have now
    items_count_query = "SELECT COUNT(*) as count FROM wardrobe_items;"
    items_count = db.execute_query(items_count_query)[0]['count']
    logger.info(f"Added wardrobe items. Total count: {items_count}")

def add_dummy_outfit_history(user_ids):
    """Add dummy outfit history records"""
    
    # Check if we already have enough outfit history
    history_count_query = "SELECT COUNT(*) as count FROM outfit_history;"
    history_count = db.execute_query(history_count_query)[0]['count']
    
    if history_count >= 10:
        logger.info(f"Already have {history_count} outfit history records, skipping creation...")
        return
    
    occasions = ['casual', 'business', 'formal', 'date', 'workout']
    weather_conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy']
    locations = ['Home', 'Office', 'Downtown', 'Restaurant', 'Park', 'Mall']
    
    for user_id in user_ids:
        # Get user's wardrobe items
        items_query = "SELECT * FROM wardrobe_items WHERE user_id = %s;"
        wardrobe_items = db.execute_query(items_query, (user_id,))
        
        if not wardrobe_items:
            continue
        
        # Create 3-5 outfit history records per user
        num_records = random.randint(3, 5)
        
        for i in range(num_records):
            # Random date in the last 30 days
            worn_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            
            # Create a random outfit with 2-4 items
            outfit_items = random.sample(list(wardrobe_items), min(random.randint(2, 4), len(wardrobe_items)))
            
            outfit_data = {
                'items': outfit_items,
                'confidence': random.randint(70, 95),
                'reason': 'Historical outfit record'
            }
            
            outfit_json = json.dumps(outfit_data)
            occasion = random.choice(occasions)
            weather = random.choice(weather_conditions)
            location = random.choice(locations)
            rating = random.randint(1, 5)
            
            insert_query = """
                INSERT INTO outfit_history 
                (user_id, outfit_data, worn_date, occasion, weather_condition, location, rating, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            db.execute_query(
                insert_query, 
                (user_id, outfit_json, worn_date, occasion, weather, location, rating, f"Outfit worn on {worn_date}"),
                fetch=False
            )
    
    # Check how many records we have now
    history_count_query = "SELECT COUNT(*) as count FROM outfit_history;"
    history_count = db.execute_query(history_count_query)[0]['count']
    logger.info(f"Added outfit history records. Total count: {history_count}")

def add_dummy_favorite_outfits(user_ids):
    """Add dummy favorite outfits"""
    
    # Check if we already have enough favorites
    favorites_count_query = "SELECT COUNT(*) as count FROM favorite_outfits;"
    favorites_count = db.execute_query(favorites_count_query)[0]['count']
    
    if favorites_count >= 10:
        logger.info(f"Already have {favorites_count} favorite outfits, skipping creation...")
        return
    
    occasions = ['casual', 'business', 'formal', 'date', 'workout']
    seasons = ['spring', 'summer', 'fall', 'winter', 'all']
    outfit_names = [
        'Weekend Casual', 'Office Look', 'Date Night', 'Summer Party', 
        'Workout Outfit', 'Evening Formal', 'Autumn Layers', 'Spring Fresh',
        'Winter Cozy', 'All-Season Favorite'
    ]
    
    for user_id in user_ids:
        # Get user's wardrobe items
        items_query = "SELECT * FROM wardrobe_items WHERE user_id = %s;"
        wardrobe_items = db.execute_query(items_query, (user_id,))
        
        if not wardrobe_items:
            continue
        
        # Create 2-4 favorite outfits per user
        num_favorites = random.randint(2, 4)
        
        for i in range(num_favorites):
            # Create a random outfit with 3-5 items
            outfit_items = random.sample(list(wardrobe_items), min(random.randint(3, 5), len(wardrobe_items)))
            
            outfit_data = json.dumps(outfit_items)
            outfit_name = random.choice(outfit_names) + f" #{random.randint(1, 100)}"
            occasion = random.choice(occasions)
            season = random.choice(seasons)
            confidence = random.randint(70, 95)
            times_worn = random.randint(0, 10)
            
            # Weather context
            weather_context = {
                'temperature': random.randint(5, 35),
                'condition': random.choice(['sunny', 'cloudy', 'rainy', 'partly cloudy']),
                'humidity': random.randint(30, 80),
                'windSpeed': random.randint(0, 30)
            }
            weather_json = json.dumps(weather_context)
            
            # Random last worn date (some may be None)
            last_worn = None
            if times_worn > 0:
                last_worn = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            
            insert_query = """
                INSERT INTO favorite_outfits 
                (user_id, outfit_name, outfit_data, occasion, season, weather_context, 
                confidence_score, notes, times_worn, last_worn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            db.execute_query(
                insert_query, 
                (
                    user_id, outfit_name, outfit_data, occasion, season, weather_json,
                    confidence, f"My favorite {occasion} outfit", times_worn, last_worn
                ),
                fetch=False
            )
    
    # Check how many records we have now
    favorites_count_query = "SELECT COUNT(*) as count FROM favorite_outfits;"
    favorites_count = db.execute_query(favorites_count_query)[0]['count']
    logger.info(f"Added favorite outfits. Total count: {favorites_count}")

def add_dummy_trip_plans(user_ids):
    """Add dummy trip plans"""
    
    # Check if we already have enough trip plans
    trips_count_query = "SELECT COUNT(*) as count FROM trip_plans;"
    trips_count = db.execute_query(trips_count_query)[0]['count'] if db.execute_query(trips_count_query) else 0
    
    if trips_count >= 5:
        logger.info(f"Already have {trips_count} trip plans, skipping creation...")
        return
    
    # If trip_plans table doesn't exist, skip
    table_check_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'trip_plans'
        );
    """
    table_exists = db.execute_query(table_check_query)
    if not table_exists or not table_exists[0]['exists']:
        logger.info("Trip plans table doesn't exist, skipping...")
        return
    
    destinations = [
        'New York City', 'Miami Beach', 'Los Angeles', 'Paris, France',
        'Tokyo, Japan', 'London, UK', 'Barcelona, Spain', 'Sydney, Australia'
    ]
    
    activities = [
        'Sightseeing', 'Beach day', 'Museum visits', 'Shopping',
        'Hiking', 'Fine dining', 'Business meetings', 'Family visit'
    ]
    
    for user_id in user_ids:
        # Create 1-3 trip plans per user
        num_trips = random.randint(1, 3)
        
        for i in range(num_trips):
            # Random dates in the future
            start_offset = random.randint(7, 90)
            duration = random.randint(3, 14)
            
            start_date = (datetime.now() + timedelta(days=start_offset)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=start_offset + duration)).strftime('%Y-%m-%d')
            
            destination = random.choice(destinations)
            trip_name = f"Trip to {destination}"
            
            # Random activities
            trip_activities = random.sample(activities, random.randint(2, 5))
            activities_json = json.dumps(trip_activities)
            
            # Random weather forecast
            weather_forecast = {
                'temperature_high': random.randint(15, 35),
                'temperature_low': random.randint(5, 25),
                'conditions': random.choice(['sunny', 'cloudy', 'rainy', 'mixed'])
            }
            weather_json = json.dumps(weather_forecast)
            
            # Random packing list items
            clothing_items = ['T-shirts', 'Jeans', 'Shorts', 'Dress shirts', 'Swimwear', 
                            'Jackets', 'Formal wear', 'Shoes', 'Socks', 'Underwear']
            essentials = ['Passport', 'Phone charger', 'Toiletries', 'Medications', 'Camera']
            
            packing_list = {
                'clothing': random.sample(clothing_items, random.randint(3, 8)),
                'essentials': random.sample(essentials, random.randint(2, 5))
            }
            packing_json = json.dumps(packing_list)
            
            is_completed = random.random() < 0.3  # 30% chance of being completed
            
            insert_query = """
                INSERT INTO trip_plans 
                (user_id, trip_name, destination, start_date, end_date, 
                weather_forecast, activities, packing_list, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            try:
                db.execute_query(
                    insert_query, 
                    (
                        user_id, trip_name, destination, start_date, end_date,
                        weather_json, activities_json, packing_json, is_completed
                    ),
                    fetch=False
                )
            except Exception as e:
                logger.error(f"Error adding trip plan: {e}")
    
    # Check how many records we have now
    trips_count_query = "SELECT COUNT(*) as count FROM trip_plans;"
    trips_count = db.execute_query(trips_count_query)[0]['count'] if db.execute_query(trips_count_query) else 0
    logger.info(f"Added trip plans. Total count: {trips_count}")

def show_database_summary():
    """Show a summary of the database tables and record counts"""
    try:
        # Get all tables in the public schema
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        tables = db.execute_query(query)
        
        print("\n=== DATABASE SUMMARY ===")
        print(f"Total tables: {len(tables)}")
        
        for table in tables:
            table_name = table['table_name']
            
            # Count rows in table
            count_query = f"SELECT COUNT(*) as row_count FROM {table_name};"
            try:
                count_result = db.execute_query(count_query)
                row_count = count_result[0]['row_count'] if count_result else 0
                print(f"- {table_name}: {row_count} records")
            except Exception as e:
                print(f"- {table_name}: Error counting records - {e}")
            
    except Exception as e:
        logger.error(f"Error generating database summary: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Adding dummy data to the Styra database...")
    
    if add_dummy_data():
        print("\nDummy data added successfully!")
        show_database_summary()
    else:
        print("\nFailed to add dummy data. Check the logs for errors.")
