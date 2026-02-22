CREATE TABLE Category (id INTEGER PRIMARY KEY, 
                        name TEXT NOT NULL, 
                        description TEXT, 
                        create_at TEXT DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        
                        
CREATE TABLE Habit (id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL, 
                    description TEXT, 
                    category_id INTEGER NOT NULL, 
                    create_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES Category(id)
                    );


CREATE TABLE HabitLog( id INTEGER PRIMARY KEY, 
                        habit_id INTEGER NOT NULL, 
                        done INTEGER NOT NULL DEFAULT 0,
                        complete_at TEXT,
                        date TEXT NOT NULL DEFAULT CURRENT_DATE,
                        UNIQUE(habit_id, date),
                        FOREIGN KEY (habit_id) REFERENCES Habit(id)
                        );

CREATE TABLE HabitSchedule( id INTEGER PRIMARY KEY,
                            habit_id INTEGER NOT NULL,
                            day_of_the_week INTEGER,
                            FOREIGN KEY (habit_id) REFERENCES Habit(id)
                            );

CREATE TABLE HabitHistory (id INTEGER PRIMARY KEY,
                    habit_id,
                    name TEXT NOT NULL, 
                    description TEXT, 
                    category_id INTEGER NOT NULL, 
                    create_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    delete_date TEXT,
                    FOREIGN KEY (category_id) REFERENCES Category(id)
                    );

CREATE TABLE Settings ( key TEXT NOT NULL , 
                        value TEXT , 
                        create_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
