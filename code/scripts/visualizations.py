# VISUALIZATIONS !!

# initial distribution of citation type

citation_counts = citations_2019['violation_description'].value_counts().head(10)
citation_counts = citation_counts.sort_values(ascending=False)

colors = ['darkred' if 'No Parking' in label or 'Street Cleaning' in label else 'lightcoral'
          for label in citation_counts.index]

fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
ax = citation_counts.plot(kind='barh', color=colors, ax=ax, title='Top 10 Violation Types in 2019')
ax.set_xlabel('Count', size=14, labelpad=10)
ax.set_ylabel('Violation Description', size=14, labelpad=10)
ax.tick_params(labelsize=12)
plt.gca().invert_yaxis()
plt.tight_layout()
fig.savefig('citations_top10_highres.png', dpi=300, bbox_inches='tight')
plt.show()


# choropleth map of neighborhood citation counts
neighborhood_citations = neighborhoods.merge(
    neighborhood_agg[['neighborhood', 'citation_count']],
    left_on='name',
    right_on='neighborhood',
    how='left'
)
neighborhood_citations['citation_count'] = neighborhood_citations['citation_count'].fillna(0)

fig, ax = plt.subplots(figsize=(14, 11), dpi=200)
neighborhood_citations.plot(
    column='citation_count',
    cmap='Purples',
    linewidth=0.6,
    edgecolor='black',
    legend=True,
    legend_kwds={'label': 'Citation Count', 'shrink': 0.7},
    ax=ax
)
ax.set_title('2019 Parking Citation Count by LA Neighborhood (N = 10,000)', fontsize=18)
ax.set_axis_off()
plt.tight_layout()
fig.savefig('la_neighborhood_citations_choropleth_highres.png', dpi=300, bbox_inches='tight')
plt.show()


# interactive chloropleth map that can be opened in new tab

# base map centered on LA
la_map = folium.Map(location=[34.0522, -118.2437], zoom_start=10)

Choropleth(
    geo_data=neighborhood_citations,
    name='choropleth',
    data=neighborhood_citations,
    columns=['name', 'citation_count'],
    key_on='feature.properties.name',
    fill_color='Purples',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='2019 Parking Citation Count'
).add_to(la_map)

folium.LayerControl().add_to(la_map)

# saving to html
#la_map.save('la_parking_citations_choropleth.html')