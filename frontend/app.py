import json
import streamlit as st
import requests

st.title("AI Employee Assistant")
query = st.text_input("Enter query:")

if st.button("Send"):
    placeholder = st.empty()
    full_response = ""

    # Sending Post request to backend
    with requests.post("http://localhost:8000/user",
                       json={"query": query},
                       stream=True) as response:

        for line in response.iter_lines():
            if line:
                # decode bytes to string
                decoded_line = line.decode('utf-8')

                # STRIP "data: " prefix if your FastAPI adds it
                if decoded_line.startswith("data: "):
                    decoded_line = decoded_line.replace("data: ", "").strip()

                try:
                    # parse JSON
                    data = json.loads(decoded_line)

                    if "response" in data:
                        # Append the token
                        full_response += data["response"]
                        # Render Markdown with a cursor
                        placeholder.markdown(full_response + "|")

                    elif "error" in data:
                        st.error(f"Backend Error: {data['error']}")

                except json.JSONDecodeError:
                    print(f"Skipping unparseable line: {decoded_line}")

    # Final render
    placeholder.markdown(full_response)
