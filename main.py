# -*- coding: utf-8 -*-
"""
TTOKEN ESCRITORIO - MVP PYTHON/KIVY
Abra este arquivo no Pydroid 3 e toque em Executar.

Dependencia:
    pip install kivy

Opcional:
    Coloque um video chamado background.mp4 na mesma pasta deste arquivo.
    O video de fundo depende do suporte de video disponivel no Android/Pydroid.

Este MVP funciona localmente. Conexoes reais com redes sociais, IA online,
edicao/exportacao de MP4 e publicacao exigem integracoes externas.
"""

import os
import json
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle

try:
    from kivy.uix.video import Video
except Exception:
    Video = None

try:
    from plyer import notification
except Exception:
    notification = None


# ---------- Aparencia ----------
Window.clearcolor = (0.035, 0.055, 0.09, 1)

AZUL = (0.08, 0.38, 0.78, 1)
AZUL_ESCURO = (0.035, 0.075, 0.14, 0.96)
LARANJA = (1.0, 0.48, 0.12, 1)
BRANCO = (0.95, 0.97, 1, 1)
CINZA = (0.68, 0.74, 0.82, 1)
VERDE = (0.15, 0.72, 0.42, 1)
VERMELHO = (0.82, 0.20, 0.20, 1)

AGENTES = {
    "Engajamento": [
        "Caçador de tendências",
        "Extrator de referências",
        "Otimizador de engajamento",
    ],
    "Venda": [
        "Pesquisador de nicho e produto",
        "Roteirista de vendas",
        "Estrategista comercial",
    ],
}


def texto_widget(texto, tamanho=16, cor=BRANCO, altura=None, **kwargs):
    lbl = Label(
        text=str(texto),
        color=cor,
        font_size=dp(tamanho),
        halign="center",
        valign="middle",
        size_hint_y=None if altura else 1,
        height=dp(altura) if altura else None,
        **kwargs
    )
    lbl.bind(size=lambda obj, val: setattr(obj, "text_size", (val[0] - dp(12), None)))
    return lbl


class Botao(Button):
    def __init__(self, texto, cor=AZUL, **kwargs):
        super().__init__(**kwargs)
        self.text = texto
        self.background_normal = ""
        self.background_down = ""
        self.background_color = cor
        self.color = BRANCO
        self.font_size = dp(15)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)


class Campo(TextInput):
    def __init__(self, dica="", multiline=False, **kwargs):
        super().__init__(**kwargs)
        self.hint_text = dica
        self.multiline = multiline
        self.size_hint_y = None
        self.height = dp(46 if not multiline else 100)
        self.padding = [dp(12), dp(12), dp(12), dp(10)]
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0.93, 0.95, 0.98, 1)
        self.foreground_color = (0.06, 0.09, 0.14, 1)
        self.cursor_color = (0.05, 0.2, 0.5, 1)
        self.font_size = dp(14)


class Painel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)
        with self.canvas.before:
            Color(*AZUL_ESCURO)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._atualizar_bg, size=self._atualizar_bg)

    def _atualizar_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size


class TTokenApp(App):
    def build(self):
        self.title = "Ttoken Escritório"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.arquivo_dados = os.path.join(self.base_dir, "ttoken_dados.json")
        self.dados = self.carregar_dados()
        self.linha_atual = "Engajamento"
        self.indice_agente = 0
        self.video_fundo = None

        raiz = FloatLayout()

        caminho_video = os.path.join(self.base_dir, "background.mp4")
        if Video is not None and os.path.exists(caminho_video):
            try:
                self.video_fundo = Video(
                    source=caminho_video,
                    state="play",
                    options={"eos": "loop"},
                    volume=0,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint=(1, 1),
                    pos_hint={"x": 0, "y": 0},
                )
                raiz.add_widget(self.video_fundo)
            except Exception as erro:
                print("Não foi possível iniciar o vídeo de fundo:", erro)

        # Camada escura para manter os textos legíveis.
        with raiz.canvas.before:
            Color(0.015, 0.035, 0.075, 0.78)
            self.fundo = Rectangle(pos=raiz.pos, size=raiz.size)
        raiz.bind(pos=self._ajustar_fundo, size=self._ajustar_fundo)

        self.sm = ScreenManager(transition=FadeTransition())
        raiz.add_widget(self.sm)

        self.criar_telas()
        self.sm.current = "inicio"
        return raiz

    def _ajustar_fundo(self, widget, *_):
        self.fundo.pos = widget.pos
        self.fundo.size = widget.size

    def carregar_dados(self):
        padrao = {
            "historico": [],
            "pontuacao": {},
            "contas": {},
            "rascunhos": [],
            "maestro": 0,
        }
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, "r", encoding="utf-8") as arq:
                    recebido = json.load(arq)
                if isinstance(recebido, dict):
                    padrao.update(recebido)
        except Exception as erro:
            print("Aviso ao ler dados locais:", erro)
        return padrao

    def salvar(self):
        try:
            with open(self.arquivo_dados, "w", encoding="utf-8") as arq:
                json.dump(self.dados, arq, ensure_ascii=False, indent=2)
        except Exception as erro:
            self.aviso("Não foi possível salvar os dados: " + str(erro))

    def aviso(self, mensagem, titulo="Ttoken Escritório"):
        caixa = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        caixa.add_widget(texto_widget(mensagem, 14, (0.08, 0.1, 0.15, 1)))
        fechar = Botao("Entendi", AZUL)
        caixa.add_widget(fechar)
        popup = Popup(title=titulo, content=caixa, size_hint=(0.88, None), height=dp(220))
        fechar.bind(on_release=popup.dismiss)
        popup.open()

    def notificar(self, titulo, mensagem):
        if notification:
            try:
                notification.notify(title=titulo, message=mensagem, app_name="Ttoken")
                return
            except Exception as erro:
                print("Notificação indisponível:", erro)
        print(titulo + ": " + mensagem)

    def criar_telas(self):
        self.sm.add_widget(self.tela_inicio())
        self.sm.add_widget(self.tela_linhas())
        self.sm.add_widget(self.tela_contas())
        self.sm.add_widget(self.tela_editor())
        self.sm.add_widget(self.tela_resultados())
        self.sm.add_widget(self.tela_aprovacao())

    def nova_tela(self, nome, titulo):
        tela = Screen(name=nome)
        painel = Painel()
        painel.add_widget(texto_widget(titulo, 23, LARANJA, 42))
        tela.add_widget(painel)
        tela.painel = painel
        return tela

    def adicionar_voltar(self, painel):
        btn = Botao("← VOLTAR AO INÍCIO", (0.20, 0.24, 0.32, 1))
        btn.bind(on_release=lambda *_: self.ir("inicio"))
        painel.add_widget(btn)

    def tela_inicio(self):
        tela = self.nova_tela("inicio", "TTOKEN ESCRITÓRIO")
        p = tela.painel
        p.add_widget(texto_widget("Seu escritório inteligente de conteúdo e vendas", 14, CINZA, 48))
        p.add_widget(texto_widget("MAESTRO", 19, BRANCO, 34))
        p.add_widget(texto_widget("O Maestro organiza as tarefas e coordena os agentes.", 13, CINZA, 42))
        b = Botao("INICIAR ESCRITÓRIO", AZUL)
        b.bind(on_release=lambda *_: self.ir("linhas"))
        p.add_widget(b)
        b = Botao("CONECTAR CONTAS", LARANJA)
        b.bind(on_release=lambda *_: self.ir("contas"))
        p.add_widget(b)
        b = Botao("EDITOR DE CONTEÚDO", AZUL)
        b.bind(on_release=lambda *_: self.ir("editor"))
        p.add_widget(b)
        b = Botao("RESULTADOS E EVOLUÇÃO", (0.20, 0.48, 0.34, 1))
        b.bind(on_release=lambda *_: self.atualizar_resultados())
        p.add_widget(b)
        p.add_widget(texto_widget("MVP local • publicação sempre depende da sua aprovação", 11, CINZA, 40))
        return tela

    def tela_linhas(self):
        tela = self.nova_tela("linhas", "ESCOLHA A LINHA DE TRABALHO")
        p = tela.painel
        p.add_widget(texto_widget("O Maestro vai coordenar os agentes da linha escolhida.", 13, CINZA, 48))
        b = Botao("ENGAJAMENTO — VISUALIZAÇÕES E CURTIDAS", AZUL)
        b.bind(on_release=lambda *_: self.iniciar_linha("Engajamento"))
        p.add_widget(b)
        b = Botao("VENDA — CONVERSÃO E CLIENTES", LARANJA)
        b.bind(on_release=lambda *_: self.iniciar_linha("Venda"))
        p.add_widget(b)
        self.adicionar_voltar(p)
        return tela

    def iniciar_linha(self, linha):
        self.linha_atual = linha
        self.indice_agente = 0
        self.log_execucao = []
        self.painel_execucao = Painel()
        self.painel_execucao.add_widget(texto_widget("MAESTRO EM AÇÃO", 22, LARANJA, 44))
        self.painel_execucao.add_widget(texto_widget("Linha: " + linha, 15, BRANCO, 32))
        self.status_agente = texto_widget("Preparando equipe...", 16, CINZA, 70)
        self.painel_execucao.add_widget(self.status_agente)
        tela = Screen(name="execucao")
        tela.add_widget(self.painel_execucao)
        if self.sm.has_screen("execucao"):
            self.sm.remove_widget(self.sm.get_screen("execucao"))
        self.sm.add_widget(tela)
        self.ir("execucao")
        Clock.schedule_once(self.executar_proximo_agente, 0.8)

    def executar_proximo_agente(self, *_):
        equipe = AGENTES[self.linha_atual]
        if self.indice_agente < len(equipe):
            nome = equipe[self.indice_agente]
            self.log_execucao.append(nome + " — tarefa demonstrativa concluída")
            self.status_agente.text = "Agente " + str(self.indice_agente + 1) + "/" + str(len(equipe)) + "\n" + nome + "\nAnalisando e organizando..."
            self.indice_agente += 1
            Clock.schedule_once(self.executar_proximo_agente, 1.1)
        else:
            self.dados["historico"].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "linha": self.linha_atual,
                "agentes": self.log_execucao,
                "status": "Aguardando aprovação",
            })
            self.salvar()
            self.status_agente.text = "Análise demonstrativa concluída.\nO conteúdo está aguardando sua aprovação."
            btn = Botao("REVISAR E APROVAR CONTEÚDO", VERDE)
            btn.bind(on_release=lambda *_: self.ir("aprovacao"))
            self.painel_execucao.add_widget(btn)
            btn2 = Botao("VOLTAR AO INÍCIO", (0.20, 0.24, 0.32, 1))
            btn2.bind(on_release=lambda *_: self.ir("inicio"))
            self.painel_execucao.add_widget(btn2)
            self.notificar("Ttoken", "A análise terminou. Revise o conteúdo antes de publicar.")

    def tela_aprovacao(self):
        tela = self.nova_tela("aprovacao", "APROVAÇÃO DO USUÁRIO")
        p = tela.painel
        p.add_widget(texto_widget("Nenhum conteúdo será publicado por este protótipo.", 14, CINZA, 54))
        p.add_widget(texto_widget("Revise a ideia e registre sua decisão:", 14, BRANCO, 38))
        b = Botao("APROVAR RASCUNHO", VERDE)
        b.bind(on_release=lambda *_: self.registrar_decisao("Aprovado pelo usuário — ainda não publicado"))
        p.add_widget(b)
        b = Botao("RECUSAR RASCUNHO", VERMELHO)
        b.bind(on_release=lambda *_: self.registrar_decisao("Recusado pelo usuário"))
        p.add_widget(b)
        self.adicionar_voltar(p)
        return tela

    def registrar_decisao(self, decisao):
        self.dados["historico"].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "linha": self.linha_atual,
            "status": decisao,
        })
        self.salvar()
        self.aviso(decisao + ". Nenhuma publicação foi feita.")
        self.ir("inicio")

    def tela_contas(self):
        tela = self.nova_tela("contas", "CONTAS E REDES SOCIAIS")
        p = tela.painel
        p.add_widget(texto_widget("Este protótipo não solicita nem armazena senhas.", 13, CINZA, 44))
        self.campos_contas = {}
        for rede in ("TikTok", "YouTube", "Instagram"):
            p.add_widget(texto_widget(rede, 15, LARANJA, 28))
            campo = Campo("Nome de usuário ou e-mail (opcional)")
            self.campos_contas[rede] = campo
            p.add_widget(campo)
        b = Botao("SALVAR ANOTAÇÕES", AZUL)
        b.bind(on_release=lambda *_: self.salvar_contas())
        p.add_widget(b)
        p.add_widget(texto_widget("Login oficial por OAuth ainda precisa ser integrado.", 11, CINZA, 38))
        self.adicionar_voltar(p)
        return tela

    def salvar_contas(self):
        self.dados["contas"] = {rede: campo.text.strip() for rede, campo in self.campos_contas.items()}
        self.salvar()
        self.aviso("Anotações das contas salvas neste aparelho. Isso não conecta as redes sociais.")

    def tela_editor(self):
        tela = self.nova_tela("editor", "EDITOR DE CONTEÚDO")
        p = tela.painel
        self.arquivo_video = ""
        self.rotulo_arquivo = texto_widget("Nenhum vídeo selecionado", 12, CINZA, 40)
        b = Botao("ESCOLHER VÍDEO DO CELULAR", AZUL)
        b.bind(on_release=lambda *_: self.abrir_seletor_video())
        p.add_widget(b)
        p.add_widget(self.rotulo_arquivo)
        self.campo_url = Campo("Ou cole aqui o link do vídeo")
        p.add_widget(self.campo_url)
        self.campo_legenda = Campo("Legenda / descrição", multiline=True)
        p.add_widget(self.campo_legenda)
        self.campo_produto = Campo("Produto ou tema")
        p.add_widget(self.campo_produto)
        self.campo_cta = Campo("Chamada para ação (ex.: peça agora)")
        p.add_widget(self.campo_cta)
        b = Botao("SALVAR RASCUNHO", LARANJA)
        b.bind(on_release=lambda *_: self.salvar_rascunho())
        p.add_widget(b)
        p.add_widget(texto_widget("Este editor salva os dados; ainda não corta nem exporta MP4.", 11, CINZA, 38))
        self.adicionar_voltar(p)
        return tela

    def abrir_seletor_video(self):
        seletor = FileChooserListView(
            path="/storage/emulated/0",
            filters=["*.mp4", "*.mov", "*.m4v", "*.3gp"],
            multiselect=False,
        )
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        layout.add_widget(seletor)
        botoes = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        popup = Popup(title="Selecione um vídeo", content=layout, size_hint=(0.95, 0.9))
        cancelar = Botao("Cancelar", VERMELHO)
        escolher = Botao("Usar vídeo", VERDE)
        botoes.add_widget(cancelar)
        botoes.add_widget(escolher)
        layout.add_widget(botoes)
        cancelar.bind(on_release=popup.dismiss)

        def confirmar(*_):
            if seletor.selection:
                self.arquivo_video = seletor.selection[0]
                self.rotulo_arquivo.text = os.path.basename(self.arquivo_video)
            popup.dismiss()

        escolher.bind(on_release=confirmar)
        popup.open()

    def salvar_rascunho(self):
        rascunho = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "video": self.arquivo_video,
            "url": self.campo_url.text.strip(),
            "legenda": self.campo_legenda.text.strip(),
            "produto": self.campo_produto.text.strip(),
            "cta": self.campo_cta.text.strip(),
        }
        self.dados["rascunhos"].append(rascunho)
        self.salvar()
        self.aviso("Rascunho salvo neste aparelho. A edição e exportação do vídeo ainda não estão implementadas.")

    def tela_resultados(self):
        tela = self.nova_tela("resultados", "RESULTADOS E EVOLUÇÃO")
        self.painel_resultados = tela.painel
        self.adicionar_voltar(self.painel_resultados)
        return tela

    def atualizar_resultados(self):
        p = self.painel_resultados
        # Mantém título e botão voltar, remove conteúdo antigo no meio.
        while len(p.children) > 2:
            p.remove_widget(p.children[0])
        p.add_widget(texto_widget("Pontuação demonstrativa dos agentes", 14, CINZA, 36), index=0)
        pontos = self.dados.get("pontuacao", {})
        if not pontos:
            p.add_widget(texto_widget("Ainda não há pontuações. Use os botões abaixo para testar.", 12, CINZA, 48), index=0)
        else:
            for nome, valor in sorted(pontos.items(), key=lambda item: item[1], reverse=True):
                p.add_widget(texto_widget(nome + ": " + str(valor) + " pontos", 14, BRANCO, 32), index=0)
        grade = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(96))
        grade.add_widget(Botao("+5 tendência", AZUL, on_release=lambda *_: self.adicionar_pontos("Caçador de tendências", 5)))
        grade.add_widget(Botao("+5 vendas", LARANJA, on_release=lambda *_: self.adicionar_pontos("Estrategista comercial", 5)))
        p.add_widget(grade, index=0)
        self.ir("resultados")

    def adicionar_pontos(self, agente, quantidade):
        pontos = self.dados.setdefault("pontuacao", {})
        pontos[agente] = int(pontos.get(agente, 0)) + quantidade
        self.dados["maestro"] = int(self.dados.get("maestro", 0)) + quantidade
        self.salvar()
        self.atualizar_resultados()

    def ir(self, nome):
        self.sm.current = nome

    def on_pause(self):
        self.salvar()
        return True

    def on_stop(self):
        self.salvar()


if __name__ == "__main__":
    TTokenApp().run()
