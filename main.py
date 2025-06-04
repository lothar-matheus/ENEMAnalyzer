import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime
import os
import warnings

warnings.filterwarnings('ignore')


class ENEMAnalyzer:
    """
    Classe principal para análise dos dados do ENEM 2023
    Versão standalone sem dependência do Streamlit
    """

    def _init_(self, arquivo_dados="MICRODADOS_ENEM_2023.csv"):
        self.arquivo_dados = arquivo_dados
        self.dados = None
        self.dados_processados = False

        # Mapeamentos para melhorar a legibilidade
        self.map_sexo = {1: 'Masculino', 2: 'Feminino'}
        self.map_cor_raca = {
            1: 'Não declarado', 2: 'Branca', 3: 'Preta',
            4: 'Parda', 5: 'Amarela', 6: 'Indígena'
        }
        self.map_tp_escola = {1: 'Não Respondeu', 2: 'Pública', 3: 'Privada'}
        self.map_dependencia = {
            1: 'Federal', 2: 'Estadual', 3: 'Municipal', 4: 'Privada'
        }

        # Mapeamento de regiões
        self.regioes = {
            'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte',
            'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
            'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }

    def carregar_dados(self, amostra=None):
        """
        Carrega os dados do ENEM
        amostra: número de linhas para carregar (None = todos os dados)
        """
        print(f"📂 Carregando dados de {self.arquivo_dados}...")

        if not os.path.exists(self.arquivo_dados):
            print(f"❌ Arquivo não encontrado: {self.arquivo_dados}")
            print("💡 Certifique-se de que o arquivo está na pasta correta")
            return False

        try:
            # Carregar dados com encoding adequado
            self.dados = pd.read_csv(
                self.arquivo_dados,
                sep=';',
                encoding='latin-1',
                nrows=amostra,
                low_memory=False
            )

            print(f"✅ Dados carregados: {len(self.dados):,} registros")
            print(f"📊 Colunas disponíveis: {len(self.dados.columns)}")

            return True

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def processar_dados(self):
        """
        Processa e limpa os dados para análise
        """
        if self.dados is None:
            print("❌ Dados não carregados. Execute carregar_dados() primeiro.")
            return False

        print("🔄 Processando dados...")

        # Aplicar mapeamentos
        if 'TP_SEXO' in self.dados.columns:
            self.dados['SEXO'] = self.dados['TP_SEXO'].map(self.map_sexo)

        if 'TP_COR_RACA' in self.dados.columns:
            self.dados['COR_RACA'] = self.dados['TP_COR_RACA'].map(self.map_cor_raca)

        if 'TP_ESCOLA' in self.dados.columns:
            self.dados['TIPO_ESCOLA'] = self.dados['TP_ESCOLA'].map(self.map_tp_escola)

        if 'TP_DEPENDENCIA_ADM_ESC' in self.dados.columns:
            self.dados['DEPENDENCIA_ESCOLA'] = self.dados['TP_DEPENDENCIA_ADM_ESC'].map(self.map_dependencia)

        # Adicionar região
        if 'SG_UF_ESC' in self.dados.columns:
            self.dados['REGIAO'] = self.dados['SG_UF_ESC'].map(self.regioes)
        elif 'CO_UF_ESC' in self.dados.columns:
            # Mapear código da UF para sigla (se necessário)
            pass

        # Criar faixas etárias
        if 'NU_IDADE' in self.dados.columns:
            self.dados['FAIXA_ETARIA'] = pd.cut(
                self.dados['NU_IDADE'],
                bins=[0, 17, 19, 21, 25, 100],
                labels=['Menor que 18', '18-19', '20-21', '22-25', 'Mais de 25']
            )

        # Converter notas para numérico
        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        for col in colunas_notas:
            if col in self.dados.columns:
                self.dados[col] = pd.to_numeric(self.dados[col], errors='coerce')

        # Calcular média das objetivas
        objetivas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
        objetivas_existentes = [col for col in objetivas if col in self.dados.columns]

        if len(objetivas_existentes) > 0:
            self.dados['MEDIA_OBJETIVAS'] = self.dados[objetivas_existentes].mean(axis=1)

        # Criar classificação socioeconômica simplificada baseada na renda (Q006)
        if 'Q006' in self.dados.columns:
            self.dados['Q006_NUM'] = pd.to_numeric(self.dados['Q006'], errors='coerce')
            self.dados['NIVEL_SOCIOECONOMICO'] = pd.cut(
                self.dados['Q006_NUM'],
                bins=[0, 2, 4, 6, 8, 17],
                labels=['Muito Baixo', 'Baixo', 'Médio', 'Alto', 'Muito Alto']
            )

        # Filtrar apenas participantes presentes
        colunas_presenca = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
        for col in colunas_presenca:
            if col in self.dados.columns:
                self.dados = self.dados[self.dados[col] == 1]

        self.dados_processados = True
        print(f"✅ Dados processados: {len(self.dados):,} registros válidos")

        return True

    def estatisticas_gerais(self):
        """
        Exibe estatísticas gerais dos dados
        """
        if not self.dados_processados:
            print("❌ Execute processar_dados() primeiro")
            return

        print("\n" + "=" * 50)
        print("📈 ESTATÍSTICAS GERAIS - ENEM 2023")
        print("=" * 50)

        print(f"👥 Total de participantes: {len(self.dados):,}")

        # Estatísticas das notas
        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        areas_nomes = ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']

        print(f"\n📊 MÉDIAS DAS NOTAS:")
        for i, col in enumerate(colunas_notas):
            if col in self.dados.columns:
                media = self.dados[col].mean()
                desvio = self.dados[col].std()
                print(f"   {areas_nomes[i]}: {media:.1f} (±{desvio:.1f})")

        # Distribuição por sexo
        if 'SEXO' in self.dados.columns:
            print(f"\n👫 DISTRIBUIÇÃO POR SEXO:")
            dist_sexo = self.dados['SEXO'].value_counts()
            for sexo, count in dist_sexo.items():
                pct = (count / len(self.dados)) * 100
                print(f"   {sexo}: {count:,} ({pct:.1f}%)")

        # Distribuição por região
        if 'REGIAO' in self.dados.columns:
            print(f"\n🌍 DISTRIBUIÇÃO POR REGIÃO:")
            dist_regiao = self.dados['REGIAO'].value_counts()
            for regiao, count in dist_regiao.items():
                pct = (count / len(self.dados)) * 100
                print(f"   {regiao}: {count:,} ({pct:.1f}%)")

    def analise_1_desempenho_por_estado(self):
        """
        1. Desempenho médio dos alunos por Estado e região
        """
        print("\n" + "=" * 50)
        print("📍 ANÁLISE 1: Desempenho por Estado e Região")
        print("=" * 50)

        if 'SG_UF_ESC' not in self.dados.columns:
            print("❌ Coluna de UF não encontrada")
            return None

        # Calcular médias por UF e região
        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        colunas_existentes = [col for col in colunas_notas if col in self.dados.columns]

        if not colunas_existentes:
            print("❌ Nenhuma coluna de notas encontrada")
            return None

        df_estado = self.dados.groupby(['SG_UF_ESC', 'REGIAO'])[colunas_existentes].mean().round(1)
        df_estado['PARTICIPANTES'] = self.dados.groupby(['SG_UF_ESC', 'REGIAO']).size()

        print("🏆 TOP 10 ESTADOS - MÉDIA GERAL:")
        df_estado['MEDIA_GERAL'] = df_estado[colunas_existentes].mean(axis=1)
        top_estados = df_estado.nlargest(10, 'MEDIA_GERAL')[['MEDIA_GERAL', 'PARTICIPANTES']]

        for uf, row in top_estados.iterrows():
            print(f"   {uf[0]}: {row['MEDIA_GERAL']:.1f} ({row['PARTICIPANTES']:,} participantes)")

        # Criar gráfico
        df_plot = df_estado.reset_index()
        fig = px.bar(
            df_plot,
            x='SG_UF_ESC',
            y='MEDIA_GERAL',
            color='REGIAO',
            title='Desempenho Médio por Estado e Região',
            labels={'SG_UF_ESC': 'Estado', 'MEDIA_GERAL': 'Média Geral'},
            height=600
        )

        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def analise_2_desempenho_socioeconomico(self):
        """
        2. Desempenho médio dos alunos por faixa socioeconômica - CORRIGIDO
        """
        print("\n" + "=" * 50)
        print("💰 ANÁLISE 2: Desempenho por Nível Socioeconômico")
        print("=" * 50)

        # Determinar qual coluna usar para análise socioeconômica
        if 'NIVEL_SOCIOECONOMICO' in self.dados.columns and self.dados['NIVEL_SOCIOECONOMICO'].notna().sum() > 0:
            coluna_analise = 'NIVEL_SOCIOECONOMICO'
            titulo = 'Desempenho por Nível Socioeconômico'
            print("📊 Usando classificação por renda familiar (Q006)")
        elif 'DEPENDENCIA_ESCOLA' in self.dados.columns:
            coluna_analise = 'DEPENDENCIA_ESCOLA'
            titulo = 'Desempenho por Tipo de Escola'
            print("📊 Usando tipo de escola como proxy socioeconômico")
        else:
            print("❌ Dados socioeconômicos não disponíveis")
            return None

        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        colunas_existentes = [col for col in colunas_notas if col in self.dados.columns]

        if not colunas_existentes:
            print("❌ Nenhuma coluna de notas encontrada")
            return None

        # Filtrar dados válidos para a análise
        dados_validos = self.dados[self.dados[coluna_analise].notna()]
        print(f"📋 Registros válidos para análise: {len(dados_validos):,}")

        # Calcular estatísticas por grupo
        df_socio = dados_validos.groupby(coluna_analise)[colunas_existentes].agg(['mean', 'count']).round(1)

        # Contar participantes por grupo
        participantes_por_grupo = dados_validos.groupby(coluna_analise).size()

        print(f"\n📊 MÉDIAS POR {coluna_analise.upper()}:")
        for categoria in participantes_por_grupo.index:
            if pd.notna(categoria):
                n_participantes = participantes_por_grupo[categoria]
                # Calcular média geral das notas para esta categoria
                medias_categoria = dados_validos[dados_validos[coluna_analise] == categoria][colunas_existentes].mean()
                media_geral = medias_categoria.mean()

                print(f"   {categoria}: {media_geral:.1f} ({n_participantes:,} participantes)")

        # Criar gráfico - CORRIGIDO
        df_plot = dados_validos.groupby(coluna_analise)[colunas_existentes].mean().reset_index()

        df_melted = df_plot.melt(
            id_vars=[coluna_analise],
            value_vars=colunas_existentes,
            var_name='Area',
            value_name='Nota_Media'
        )

        # Mapear nomes das áreas
        area_names = {
            'NU_NOTA_CN': 'Ciências da Natureza',
            'NU_NOTA_CH': 'Ciências Humanas',
            'NU_NOTA_LC': 'Linguagens',
            'NU_NOTA_MT': 'Matemática',
            'NU_NOTA_REDACAO': 'Redação'
        }
        df_melted['Area'] = df_melted['Area'].map(area_names)

        fig = px.line(
            df_melted,
            x=coluna_analise,
            y='Nota_Media',
            color='Area',
            title=titulo,
            height=500,
            markers=True
        )

        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def analise_3_maiores_notas_redacao(self):
        """
        3. Distribuição das maiores notas de redação por estado
        """
        print("\n" + "=" * 50)
        print("✍️ ANÁLISE 3: Maiores Notas de Redação por Estado")
        print("=" * 50)

        if 'NU_NOTA_REDACAO' not in self.dados.columns:
            print("❌ Dados de redação não encontrados")
            return None

        # Top 5% das notas de redação
        percentil_95 = self.dados['NU_NOTA_REDACAO'].quantile(0.95)
        top_redacao = self.dados[self.dados['NU_NOTA_REDACAO'] >= percentil_95]

        print(f"🎯 Analisando top 5% das notas (≥ {percentil_95:.0f} pontos)")
        print(f"📝 {len(top_redacao):,} redações no top 5%")

        if 'SG_UF_ESC' in self.dados.columns:
            df_top_redacao = top_redacao.groupby('SG_UF_ESC').agg({
                'NU_NOTA_REDACAO': ['count', 'mean', 'max']
            }).round(1)

            df_top_redacao.columns = ['Quantidade', 'Media_Top', 'Nota_Maxima']
            df_top_redacao = df_top_redacao.sort_values('Quantidade', ascending=False).head(10)

            print("🏆 TOP 10 ESTADOS - MAIORES NOTAS DE REDAÇÃO:")
            for uf, row in df_top_redacao.iterrows():
                print(f"   {uf}: {row['Quantidade']} redações (máx: {row['Nota_Maxima']:.0f})")

            # Criar gráfico
            df_plot = df_top_redacao.reset_index()
            fig = px.scatter(
                df_plot,
                x='Quantidade',
                y='Media_Top',
                size='Nota_Maxima',
                hover_data=['SG_UF_ESC'],
                title='Top 5% Notas de Redação por Estado',
                labels={
                    'Quantidade': 'Número de Redações no Top 5%',
                    'Media_Top': 'Média das Notas Top 5%'
                }
            )

            return fig

        return None

    def analise_4_genero_areas(self):
        """
        4. Comparação das notas por gênero em cada área de conhecimento
        """
        print("\n" + "=" * 50)
        print("👫 ANÁLISE 4: Desempenho por Gênero nas Áreas")
        print("=" * 50)

        if 'SEXO' not in self.dados.columns:
            print("❌ Dados de sexo não encontrados")
            return None

        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        areas_nomes = ['Ciências Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']
        colunas_existentes = [col for col in colunas_notas if col in self.dados.columns]

        df_genero = self.dados.groupby('SEXO')[colunas_existentes].mean().round(1)

        print("📊 COMPARAÇÃO POR GÊNERO:")
        for i, col in enumerate(colunas_existentes):
            if len(df_genero) >= 2:
                masc = df_genero.loc['Masculino', col] if 'Masculino' in df_genero.index else 0
                fem = df_genero.loc['Feminino', col] if 'Feminino' in df_genero.index else 0
                diff = masc - fem
                area_nome = areas_nomes[colunas_notas.index(col)]
                print(f"   {area_nome}: M={masc:.1f} | F={fem:.1f} | Diff={diff:+.1f}")

        # Criar gráfico
        df_plot = df_genero.reset_index()
        df_melted = df_plot.melt(
            id_vars='SEXO',
            value_vars=colunas_existentes,
            var_name='Area',
            value_name='Nota_Media'
        )

        fig = px.bar(
            df_melted,
            x='Area',
            y='Nota_Media',
            color='SEXO',
            barmode='group',
            title='Comparação de Desempenho por Gênero',
            height=500
        )

        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def analise_5_faixa_etaria(self):
        """
        5. Distribuição das notas por faixa etária
        """
        print("\n" + "=" * 50)
        print("📅 ANÁLISE 5: Desempenho por Faixa Etária")
        print("=" * 50)

        if 'FAIXA_ETARIA' not in self.dados.columns:
            print("❌ Dados de faixa etária não processados")
            return None

        colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        colunas_existentes = [col for col in colunas_notas if col in self.dados.columns]

        df_idade = self.dados.groupby('FAIXA_ETARIA')[colunas_existentes].mean().round(1)
        df_idade['PARTICIPANTES'] = self.dados.groupby('FAIXA_ETARIA').size()

        print("📊 MÉDIAS POR FAIXA ETÁRIA:")
        for faixa, row in df_idade.iterrows():
            if pd.notna(faixa):
                media_geral = row[colunas_existentes].mean()
                print(f"   {faixa}: {media_geral:.1f} ({row['PARTICIPANTES']:,} participantes)")

        # Criar gráfico
        df_plot = df_idade.reset_index()
        df_melted = df_plot.melt(
            id_vars=['FAIXA_ETARIA', 'PARTICIPANTES'],
            value_vars=colunas_existentes,
            var_name='Area',
            value_name='Nota_Media'
        )

        fig = px.line(
            df_melted,
            x='FAIXA_ETARIA',
            y='Nota_Media',
            color='Area',
            title='Desempenho por Faixa Etária',
            height=500
        )

        return fig

    def salvar_graficos_html(self, graficos, pasta_saida="graficos_enem"):
        """
        Salva todos os gráficos em arquivos HTML
        """
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)

        print(f"\n💾 Salvando gráficos na pasta '{pasta_saida}'...")

        nomes_arquivos = [
            "01_desempenho_por_estado.html",
            "02_desempenho_socioeconomico.html",
            "03_maiores_notas_redacao.html",
            "04_comparacao_por_genero.html",
            "05_desempenho_faixa_etaria.html"
        ]

        for i, (grafico, nome) in enumerate(zip(graficos, nomes_arquivos)):
            if grafico is not None:
                caminho = os.path.join(pasta_saida, nome)
                pyo.plot(grafico, filename=caminho, auto_open=False)
                print(f"   ✅ {nome}")

        print(f"\n🎉 Gráficos salvos! Abra os arquivos HTML no navegador.")

    def executar_analise_completa(self, amostra=None, salvar_graficos=True):
        """
        Executa todas as análises
        """
        print("🚀 INICIANDO ANÁLISE COMPLETA DOS DADOS DO ENEM 2023")
        print("=" * 60)

        # Carregar e processar dados
        if not self.carregar_dados(amostra):
            return False

        if not self.processar_dados():
            return False

        # Estatísticas gerais
        self.estatisticas_gerais()

        # Executar análises
        graficos = []

        graficos.append(self.analise_1_desempenho_por_estado())
        graficos.append(self.analise_2_desempenho_socioeconomico())
        graficos.append(self.analise_3_maiores_notas_redacao())
        graficos.append(self.analise_4_genero_areas())
        graficos.append(self.analise_5_faixa_etaria())

        # Salvar gráficos
        if salvar_graficos:
            self.salvar_graficos_html([g for g in graficos if g is not None])

        print("\n" + "=" * 60)
        print("✅ ANÁLISE COMPLETA FINALIZADA!")
        print("=" * 60)

        return True


# Função principal
def main():
    """
    Função principal para executar a análise
    """
    print("📊 DASHBOARD ENEM 2023 - Análise dos Microdados")
    print("=" * 50)

    # Inicializar analisador
    analyzer = ENEMAnalyzer("MICRODADOS_ENEM_2023.csv")

    # Perguntar se quer usar amostra
    print("\n🔧 CONFIGURAÇÃO:")
    print("1. Usar todos os dados (pode ser lento)")
    print("2. Usar amostra de 100.000 registros (mais rápido)")
    print("3. Usar amostra personalizada")

    opcao = input("\nEscolha uma opção (1/2/3): ").strip()

    amostra = None
    if opcao == "2":
        amostra = 100000
    elif opcao == "3":
        try:
            amostra = int(input("Digite o número de registros: "))
        except:
            print("Valor inválido, usando todos os dados")
            amostra = None

    # Executar análise
    analyzer.executar_analise_completa(amostra=amostra)


if _name_ == "_main_":
    main()
