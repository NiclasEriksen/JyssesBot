from io import BytesIO
import discord.ui
import trusetekst
from trusetekst import H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT, V_ALIGN_TOP, V_ALIGN_CENTER, V_ALIGN_BOTTOM


class EditTextModal(discord.ui.Modal):
    text: str = ""
    def __init__(self, *args, text="", **kwargs) -> None:
        self.text = text
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Bildetekst", value=self.text))

    async def final_callback(self, modal, interaction: discord.Interaction):
        return

    async def callback(self, interaction: discord.Interaction):
        self.text = self.children[0].value
        await self.final_callback(self, interaction)


class EditSizeModal(discord.ui.Modal):
    size: int = 32
    def __init__(self, *args, size=32, **kwargs) -> None:
        self.size = size
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Fontstørrelse", value=f"{self.size}"))

    async def final_callback(self, modal, interaction: discord.Interaction):
        return

    async def callback(self, interaction: discord.Interaction):
        try:
            self.size = int(self.children[0].value)
        except Exception:
            pass
        await self.final_callback(self, interaction)


class TrusetextView(discord.ui.View):
    img_binary: BytesIO = None
    text: str = ""
    size: int = 32
    font: str = "Roboto"
    color: str = trusetekst.COLORS["red"]
    h_align: int = trusetekst.H_ALIGN_CENTER
    v_align: int = trusetekst.V_ALIGN_TOP

    font_select: discord.ui.Select = None
    color_select: discord.ui.Select = None
    edit_text_modal: EditTextModal = None
    edit_size_modal: EditSizeModal = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def build(self) -> None:
        if self.font_select is not None:
            self.remove_item(self.font_select)
        if self.color_select is not None:
            self.remove_item(self.color_select)

        self.font_select = discord.ui.Select(min_values=1, max_values=1, placeholder="Velg en font", row=0)
        self.font_select.callback = self.font_select_callback
        for f in trusetekst.fonts.font_list:
            self.font_select.add_option(
                label=f, value=f, default=f == self.font
            )

        self.color_select = discord.ui.Select(min_values=1, max_values=1, placeholder="Velg en farge", row=1)
        self.color_select.callback = self.color_select_callback
        for cn, cv in trusetekst.COLORS.items():
            self.color_select.add_option(
                label=cn, value=cv, default=cv == self.color
            )

        self.add_item(self.font_select)
        self.add_item(self.color_select)

    @discord.ui.button(label="Endre tekst", row=2, style=discord.ButtonStyle.blurple)
    async def edit_text_callback(self, _button, interaction):
        self.edit_text_modal = EditTextModal(title="Endre tekst", text=self.text)
        self.edit_text_modal.final_callback = self.edit_text_modal_callback
        await interaction.response.send_modal(self.edit_text_modal)

    async def edit_text_modal_callback(self, modal, interaction):
        self.text = modal.text
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="Endre størrelse", row=2, style=discord.ButtonStyle.blurple)
    async def edit_size_callback(self, _button, interaction):
        self.edit_size_modal = EditSizeModal(title="Endre størrelse", size=self.size)
        self.edit_size_modal.final_callback = self.edit_size_modal_callback
        await interaction.response.send_modal(self.edit_size_modal)

    async def edit_size_modal_callback(self, modal, interaction):
        self.size = modal.size
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="Post", row=2, style=discord.ButtonStyle.success)
    async def post_button_callback(self, _button, interaction: discord.Interaction):
        await self.generate_image()
        await interaction.response.edit_message(view=None, delete_after=0)
        await interaction.respond("", files=[discord.File(self.img_binary, filename="truse.png")])


    @discord.ui.button(label="Left", row=3, style=discord.ButtonStyle.secondary)
    async def hal_callback(self, _button, interaction):
        self.h_align = H_ALIGN_LEFT
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="H. Center", row=3, style=discord.ButtonStyle.secondary)
    async def hac_callback(self, _button, interaction):
        self.h_align = H_ALIGN_CENTER
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="Right", row=3, style=discord.ButtonStyle.secondary)
    async def har_callback(self, _button, interaction):
        self.h_align = H_ALIGN_RIGHT
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="Top", row=4, style=discord.ButtonStyle.secondary)
    async def vat_callback(self, _button, interaction):
        self.v_align = V_ALIGN_TOP
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="V. Center", row=4, style=discord.ButtonStyle.secondary)
    async def vac_callback(self, _button, interaction):
        self.v_align = V_ALIGN_CENTER
        await self.refresh_interaction(interaction)

    @discord.ui.button(label="Bottom", row=4, style=discord.ButtonStyle.secondary)
    async def vab_callback(self, _button, interaction):
        self.v_align = V_ALIGN_BOTTOM
        await self.refresh_interaction(interaction)


    async def refresh_interaction(self, interaction):
        await self.generate_image()
        await interaction.response.edit_message(
            files=[discord.File(self.img_binary, filename="truse.png")],
            attachments=[], view=self
        )


    async def font_select_callback(self, interaction):
        self.font = self.font_select.values[0]
        for o in self.font_select.options:
            o.default = self.font == o.value
        await self.refresh_interaction(interaction)

    async def color_select_callback(self, interaction):
        self.color = self.color_select.values[0]
        for o in self.color_select.options:
            o.default = self.color == o.value
        await self.refresh_interaction(interaction)

    async def generate_image(self):
        img = trusetekst.get_trusetext(
            self.text, self.font, self.size, self.color,
            self.v_align, self.h_align
        )

        self.img_binary = BytesIO()
        img.save(self.img_binary, format="PNG")
        self.img_binary.seek(0)
