#This file will be use to compute, none database manipulation is allowed
import numpy as np
class stat:
    def most_productive_hour(datedone):
        
        pass

class app:
    def word():
        #list of sentence
        tracker_phrases = [
                            # Positive (30%)
                            "Every small step counts.",
                            "Today is a new opportunity to grow.",
                            "You are stronger than you think.",
                            "Keep going, your efforts are paying off.",
                            "Smile and embrace the journey.",
                            "Believe in yourself and your abilities.",
                            "You are capable of amazing things.",
                            "Progress, not perfection, is the goal.",
                            "Celebrate every little achievement.",

                            # Famous Quotes (15%)
                            "Imagination is more important than knowledge. – Albert Einstein",
                            "Science is a way of thinking much more than it is a body of knowledge. – Carl Sagan",
                            "Nature is relentless and unchangeable, and it is indifferent as to whether its hidden reasons and actions are understandable to man. – Galilée",
                            "Man is condemned to be free. – Sartre",
                            "A theory is something nobody believes, except the person who made it. An experiment is something everybody believes, except the person who made it. – Max Planck",

                            # Goals (30%)
                            "Focus on what matters most today.",
                            "Break big goals into small, achievable steps.",
                            "Each day brings you closer to your dreams.",
                            "Success is built one habit at a time.",
                            "Keep your eye on the target, not the obstacle.",
                            "Progress is the sum of consistent actions.",
                            "Set clear intentions for every task.",
                            "Your future self will thank you for what you do today.",
                            "Goals are dreams with deadlines.",

                            # Discipline (15%)
                            "Discipline is the bridge between goals and achievement.",
                            "Small daily efforts create lasting results.",
                            "Consistency beats motivation every time.",
                            "Stick to your plan even when it’s tough.",
                            "True freedom comes from self-discipline.",

                            # Empathy (15%)
                            "Treat yourself with the kindness you offer others.",
                            "Understanding others begins with listening.",
                            "Compassion is a strength, not a weakness.",
                            "Offer encouragement, even on hard days.",
                            "Your empathy can change someone’s world today."
                        ]

        days_since = 10
        category_since = "Sport"
        alert = [f"It's been {days_since} days that you haven't completed a habit from {category_since} category", "It's your birthday", "Hello sunshine","You are near your goal don't give up"]
        random = np.random.randint(low=0, high= 30)
        sentence = tracker_phrases[random]
        return sentence
