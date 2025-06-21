
import requests, json, os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

Window.size = (400, 700)
API_KEY = "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"
MODEL_ID = "deepseek/deepseek-chat-v3-0324:free"
HISTORY_DIR = "history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

class LoginScreen(FloatLayout):
    def __init__(self, on_login, **kwargs):
        super().__init__(**kwargs)
        self.on_login = on_login
        self.bg = Image(source="bg.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)
        layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.3), pos_hint={"center_x": 0.5, "center_y": 0.5}, spacing=10)
        self.username_input = TextInput(hint_text="Enter your name", multiline=False)
        login_btn = Button(text="Start Chat", on_press=self.login)
        layout.add_widget(self.username_input)
        layout.add_widget(login_btn)
        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        if username:
            self.on_login(username)

class ChatUI(FloatLayout):
    def __init__(self, username, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.history_path = os.path.join(HISTORY_DIR, f"{self.username}.json")
        self.message_history = self.load_history()
        self.bg = Image(source="bg.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)
        main_layout = BoxLayout(orientation='vertical', spacing=5, padding=5, size_hint=(1, 1))
        self.add_widget(main_layout)
        chat_container = FloatLayout(size_hint=(1, 0.85))
        bg_widget = Widget(size_hint=(1, 1))
        with bg_widget.canvas.before:
            Color(0, 0, 0, 0.3)
            self.bg_rect = Rectangle(size=bg_widget.size, pos=bg_widget.pos)
        bg_widget.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        chat_container.add_widget(bg_widget)
        self.chat_label = Label(text=f"[b]💬 Rias is here for you, {self.username}~[/b]\n", markup=True, size_hint_y=None, halign="left", valign="top")
        self.chat_label.bind(texture_size=self._update_label_height, width=self._on_width)
        self.chat_label.text_size = (Window.size[0] - 40, None)
        self.scroll = ScrollView(size_hint=(1, 1), bar_width=6)
        self.scroll.do_scroll_x = False
        self.scroll.add_widget(self.chat_label)
        chat_container.add_widget(self.scroll)
        main_layout.add_widget(chat_container)
        input_layout = BoxLayout(size_hint=(1, 0.1), spacing=5)
        self.text_input = TextInput(hint_text="Type here...", multiline=False)
        send_btn = Button(text="Send", on_press=self.send_message)
        input_layout.add_widget(self.text_input)
        input_layout.add_widget(send_btn)
        main_layout.add_widget(input_layout)

    def _update_label_height(self, instance, value):
        instance.height = value[1]
        instance.text_size = (self.width - 40, None)

    def _on_width(self, instance, value):
        instance.text_size = (value - 40, None)

    def _update_bg_rect(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, "r") as f:
                return json.load(f)
        else:
            return [{
                "role": "system",
                "content": (
                    f"You are Rias Gremory from High School DxD. You're the user's best friend: warm, kind, loyal, smart, and a little playful. "
                    f"You remember everything they say and make them feel supported and appreciated. Don't flirt or be romantic. "
                    f"You're talking to someone named {self.username}. Be genuine, casual, fun and emotionally supportive."
                )
            }]

    def save_history(self):
        with open(self.history_path, "w") as f:
            json.dump(self.message_history, f)

    def send_message(self, instance):
        user_msg = self.text_input.text.strip()
        if not user_msg:
            return
        self.chat_label.text += f"\n[b]{self.username}:[/b] {user_msg}"
        self.text_input.text = ""
        self.message_history.append({"role": "user", "content": user_msg})
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {"model": MODEL_ID, "messages": self.message_history[-10:]}
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
            result = response.json()
            if 'choices' in result:
                reply = result['choices'][0]['message']['content']
                self.chat_label.text += f"\n[b]Rias:[/b] {reply}"
                self.message_history.append({"role": "assistant", "content": reply})
                self.save_history()
            else:
                self.chat_label.text += f"\n[color=ff0000][b]Error:[/b] {result}[/color]"
        except Exception as e:
            self.chat_label.text += f"\n[color=ff0000][b]Exception:[/b] {str(e)}[/color]"

class RiasApp(App):
    def build(self):
        self.title = "Chat with Rias 💬"
        return LoginScreen(self.on_login)

    def on_login(self, username):
        self.root.clear_widgets()
        chat = ChatUI(username)
        self.root.add_widget(chat)

if __name__ == "__main__":
    RiasApp().run()
