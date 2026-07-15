import gradio as gr

tabs_content = ["⚔️ Attacking Trios", "🛡 Defenders Pairs", "💼 Reserve", "🧍 Add Player", "🔎 Search"]

def responce(user_message: str, history: list):
    if user_message.strip() == "":
        return "", history

    history.append(gr.ChatMessage(role="user", content=user_message))
    history.append(gr.ChatMessage(role="assistant", content="No"))

    return "", history

with gr.Blocks() as app:
    with gr.Tab(tabs_content[0]):
        with gr.Group():
            gr.Markdown("### <center>🏆 Joueur Vedette</center>")
            gr.Image(
                value="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-9rO0Ei41-RHoO-WBXCc-N6Iwf6NXQJar1Lx7RyRHvA&s=10",
                show_label=False,
                interactive=False,
                height=200
            )

            # 2. Le bouton "piège" cliquable qui prend toute la largeur au bas de ta case
            btn_action = gr.Button("Sélectionner ce joueur", variant="primary")
    with gr.Tab(tabs_content[1]):
        pass
    with gr.Tab(tabs_content[2]):
        pass
    with gr.Tab(tabs_content[3]):
        chatbot = gr.Chatbot([gr.ChatMessage(role="assistant", content="You can start with the player name. 😄")], label="👨‍💻 The Registrar")
        msg = gr.Textbox(label="Request Input")
        msg.submit(responce, inputs=[msg, chatbot], outputs=[msg, chatbot])
    with gr.Tab(tabs_content[4]):
        gr.HTML(
            '<iframe src="https://www.hockey-reference.com/" style="width:100%; height:82vh; border:none;"></iframe>'
        )

app.launch()
