CREATE TABLE IF NOT EXISTS Category (id INTEGER PRIMARY KEY, 
                        name TEXT NOT NULL, 
                        description TEXT, 
                        create_at TEXT DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        
                        
CREATE TABLE IF NOT EXISTS Habit (id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL, 
                    description TEXT, 
                    category_id INTEGER NOT NULL,
                    is_seed INTEGER DEFAULT 0,
                    create_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES Category(id)
                    );


CREATE TABLE IF NOT EXISTS HabitLog( id INTEGER PRIMARY KEY, 
                        habit_id INTEGER NOT NULL, 
                        done INTEGER NOT NULL DEFAULT 0,
                        complete_at TEXT,
                        date TEXT NOT NULL DEFAULT CURRENT_DATE,
                        UNIQUE(habit_id, date),
                        FOREIGN KEY (habit_id) REFERENCES Habit(id)
                        );

CREATE TABLE IF NOT EXISTS HabitSchedule( id INTEGER PRIMARY KEY,
                            habit_id INTEGER NOT NULL,
                            day_of_the_week TEXT,
                            FOREIGN KEY (habit_id) REFERENCES Habit(id)
                            );

CREATE TABLE IF NOT EXISTS HabitHistory (id INTEGER PRIMARY KEY,
                    habit_id INTEGER NOT NULL,
                    name TEXT NOT NULL, 
                    description TEXT, 
                    category_id INTEGER NOT NULL, 
                    create_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    delete_date TEXT,
                    FOREIGN KEY (category_id) REFERENCES Category(id)
                    );

CREATE TABLE IF NOT EXISTS Settings ( key TEXT NOT NULL , 
                        value TEXT , 
                        create_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
