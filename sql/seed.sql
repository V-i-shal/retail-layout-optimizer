-- Seed data for testing (optional initial data)
-- This file can be run after schema.sql to populate initial sections

-- Insert store sections (26 sections A-Z in a 13x2 grid)
INSERT INTO store_section (section_id, name, x, y) VALUES
('A', 'Entrance', 0, 0),
('B', 'Fresh Produce', 1, 0),
('C', 'Bakery', 2, 0),
('D', 'Dairy', 3, 0),
('E', 'Frozen Foods', 4, 0),
('F', 'Meat & Seafood', 5, 0),
('G', 'Deli', 6, 0),
('H', 'Beverages', 7, 0),
('I', 'Snacks', 8, 0),
('J', 'Canned Goods', 9, 0),
('K', 'Condiments', 10, 0),
('L', 'Household', 11, 0),
('M', 'Checkout', 12, 0),
('N', 'Health & Beauty', 12, 1),
('O', 'Pet Supplies', 11, 1),
('P', 'Baby Products', 10, 1),
('Q', 'Cleaning', 9, 1),
('R', 'Paper Products', 8, 1),
('S', 'Pharmacy', 7, 1),
('T', 'Electronics', 6, 1),
('U', 'Books & Magazines', 5, 1),
('V', 'Toys', 4, 1),
('W', 'Seasonal', 3, 1),
('X', 'Floral', 2, 1),
('Y', 'Customer Service', 1, 1),
('Z', 'Cafe', 0, 1);

-- Insert initial run metadata
INSERT INTO run_metadata (notes) VALUES ('Database initialized');