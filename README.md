# Botmother
## Chat-Based, Module-Specific Question and Answer system

# Aim
- Allow students to ask **module-specific** questions and get **timely** and **accurate** replies. 
   - E.g. "Is it a good idea to take CS2100 in Semester 2?"
- Store questions-answer pairs in a **question bank**, and display them for each module to enable ease-of-revision and conceptual linking between similar questions
- Provide **chat-like interfaces** for these actions - such as a Telegram Bot.
- Gamification: reward students that answer correctly consistently with points and badges

# Why?
Everyone is eternally grateful to Stackoverflow/Quora/Forums in general, but university-going students demand a fast-paced learning environment. These traditonal methods either require the use of a browser or an additional app, but students likely already have Telegram or Whatsapp on their phones. A chat environment like Telegram allows for notifications, instant feedback, and a module-based system lets students see questions that are immediately relevant to their situation. 

# Flow
An example of the question-answer flow would be:

Ask question > Collect answers > Allow voting > Send votes, answers and answerer reputation/gamification information to question asker > Select correct answer > Store in Q&A bank

# Machine Learning Methods
When a user asks a question, we return the **most relevant answer** as indicated by our current machine learning models. As users rate these answers, the model improves to predict better answers for questions over time. 
   
