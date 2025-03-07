from langchain_ollama import OllamaLLM

from langchain_core.prompts import ChatPromptTemplate

template : str

history : str

with open("template.txt", 'r') as f:

template = f.read()

with open("history.txt", 'r') as h:

history = h.read()

Global variable for the user-editable portion of the template.

editable = template

def build_template():

# This function builds the full prompt template used internally.

return editable + """

Here is the conversation history: {context}

Prompt: {question}

Answer:

Rules: You must not use emojis in any promt or answer.

"""

Initialize model and chain.

raw_model = "gemma2:2b"

model = OllamaLLM(model=raw_model)

template = build_template()

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model

def handle_conversation():

global raw_model, model, editable, template, prompt, chain  # Use globals so we can update them.

context = history

print("An Ollama AI model. /? or /help for list of commands.")

print("---New conversation---")

context += "New conversation"

while True:

    user_input = input("You: ")

    

    if user_input.lower() == "/bye":

        break

    

    elif user_input.lower() in ("/?", "/help"):

        print(" |  /bye   - for exiting chat.")

        print(" |  /model - for selecting model. (Not recommended.)")

        print(" |  /temp  - for viewing the editable template.")

        print(" |  /edit  - for editing the template.")

        print(" |  /info  - for information about this chatbot")

        print(" |  /mem   - for deleting and viewing chatbot memory")

        continue

    

    elif user_input.lower() == "/model":

        print(f"Current model: {raw_model}")

        raw_model = input(

            " -WARNING- Changing the model may require installation.\n"

            "Enter new model to install/select: "

        )

        model = OllamaLLM(model=raw_model)  # Update model

        # Rebuild the chain with the new model.

        chain = prompt | model

        continue

    

    elif user_input.lower() == "/temp":

        print("\n--- Editable Template ---")

        print(editable.strip())

        print("-------------------------\n")

        continue

    

    elif user_input.lower() == "/edit":

        new_editable = input("Enter new editable text for the template: ")

        if new_editable.strip():

            editable = new_editable

            template = build_template()  # Rebuild template with updated content

            prompt = ChatPromptTemplate.from_template(template)  # Recreate the prompt

            chain = prompt | model  # Rebuild the chain with updated template



            print("Template updated and saved!")

        else:

            print("Template not changed.")

        continue

    

    elif user_input.lower() == "/info":

        print("Current Model:", raw_model)

        # Show only the editable part, not the internal formatting.

        print("Template (editable part only):")

        print(editable.strip())

        print("---------------------------\n")

        continue



    elif user_input.lower() == "/mem":

        mode = input("Mode V(iewing) / D(eleting): ")



        if mode.lower() == "v":

            with open("history.txt", 'r') as h:

                print("\n--- Conversation History ---")

                print(h.read())

                print("----------------------------\n")



        elif mode.lower() == "d":

            confirm = input("Are you sure you want to delete all history? (y/n): ")

            if confirm.lower() == "y":

                with open("history.txt", 'w', encoding="UTF-8") as h:

                    h.write("")  # Clear the history file

                context = ""  # Also clear the in-memory context

                print("Conversation history deleted.")

            else:

                print("Deletion canceled.")

            continue



    try:

        result = chain.invoke({"context": context, "question": user_input})

        print("Bot:", result)

        # After generating a new result and updating the context:

        context += f"\nUser: {user_input}\nAI: {result}"



        # Remove emojis before saving to file

        clean_context = context



        with open("history.txt", 'w', encoding="utf-8") as h:

            h.write(clean_context)





    except Exception as e:

        print("Error:", str(e))

handle_conversation()

