"""Visualisations d'exploration, fondées sur les agrégats vérifiés."""
import plotly.graph_objects as go
from ui.charts import style_chart

COLORS = ['#087f78', '#d19353', '#476eb5', '#a05f8d']
MONTHS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']


def heatmap(table, *, percent=False):
    values = table.div(table.sum(axis=1).replace(0, float('nan')), axis=0) * 100 if percent else table
    fig = go.Figure(go.Heatmap(z=values.to_numpy().tolist(), x=MONTHS, y=[str(y) for y in table.index],
        colorscale=[[0,'#f0f7f5'], [.35,'#97c8ba'], [1,'#07645f']],
        hovertemplate='%{y} · %{x}<br>%{z:.1f}' + (' % de l’année' if percent else ' articles') + '<extra></extra>',
        xgap=4, ygap=5, colorbar={'title':'%' if percent else 'Articles', 'thickness':10}))
    style_chart(fig)
    fig.update_layout(height=330, margin=dict(l=20,r=20,t=15,b=20))
    return fig


def trajectories(table, *, indexed=False):
    fig = go.Figure()
    for i, code in enumerate(table.columns):
        values = table[code]
        if indexed:
            values = values / values.iloc[0] * 100 if values.iloc[0] else values * float('nan')
        fig.add_trace(go.Scatter(x=table.index.tolist(), y=values.tolist(), name=code,
            mode='lines+markers', line={'width':3,'color':COLORS[i % len(COLORS)]},
            hovertemplate=code+' · %{x}<br>%{y:.1f}<extra></extra>'))
    style_chart(fig)
    fig.update_layout(showlegend=True,legend={'orientation':'h','y':1.18},height=340,
        yaxis_title='Indice (première année = 100)' if indexed else 'Articles',xaxis_title='Année')
    fig.update_xaxes(dtick=1)
    return fig


def seasonality(table):
    fig=go.Figure(go.Bar(x=MONTHS, y=table.sum(axis=0).tolist(), marker_color='#d19353',
        hovertemplate='%{x}<br>%{y:,} dépôts<extra></extra>'))
    style_chart(fig)
    fig.update_layout(height=300, yaxis_title='Articles · toutes les années filtrées')
    return fig


def overlap_chart(table, *, percent=False):
    fig=go.Figure(go.Heatmap(z=table.to_numpy().tolist(), x=table.columns.tolist(),y=table.index.tolist(),
        colorscale=[[0,'#f0f7f5'],[1,'#087f78']],texttemplate='%{z:.1f}' if percent else '%{z:,.0f}',
        hovertemplate='%{y} ∩ %{x}<br>%{z:.1f}'+(' % de Jaccard' if percent else ' articles')+'<extra></extra>',
        colorbar={'thickness':10,'title':'%' if percent else 'Articles'},xgap=5,ygap=5))
    style_chart(fig)
    fig.update_layout(height=350)
    return fig


def combinations_chart(table):
    labels=table['combination'].tolist()
    fig=go.Figure(go.Treemap(labels=['Tous les articles']+labels,
        parents=['']+['Tous les articles']*len(labels),
        values=[int(table['articles'].sum())]+table['articles'].tolist(), branchvalues='total',
        marker={'colors':['#eef4f3']+[COLORS[i%4] for i in range(len(labels))]},
        textinfo='label+value', hovertemplate='%{label}<br>%{value:,} articles<extra></extra>'))
    style_chart(fig)
    fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
    return fig


def vocabulary_chart(table):
    ordered=table.iloc[::-1]
    fig=go.Figure(go.Bar(x=ordered['articles'].tolist(),y=ordered['term'].tolist(),orientation='h',marker_color='#476eb5',
        hovertemplate='%{y}<br>%{x:,} titres<extra></extra>'))
    style_chart(fig)
    fig.update_layout(height=max(350, len(table)*24),xaxis_title='Titres contenant le mot',margin=dict(l=10,r=10,t=10,b=20))
    return fig


def terms_chart(series, *, normalized=False):
    fig=go.Figure()
    for i,(term,values) in enumerate(series.items()):
        fig.add_trace(go.Scatter(x=values.index.tolist(),y=values.tolist(),mode='lines+markers',name=term,
            line={'color':COLORS[i%4],'width':3}))
    style_chart(fig)
    fig.update_layout(showlegend=True,legend={'orientation':'h','y':1.18},height=350,
        yaxis_title='Titres pour 1 000 articles' if normalized else 'Titres',xaxis_title='Année')
    fig.update_xaxes(dtick=1)
    return fig
