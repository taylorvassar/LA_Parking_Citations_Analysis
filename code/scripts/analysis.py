### DATA MODELING - NEIGHBORHOOD-LEVEL AGGREGATION
# goal: aggregate citations by neighborhood and build a negative binomial regression model
# predicting citation count using aggregated variables including the categorical variables


# neighborhood-level dataset
neighborhood_agg = citations_2019.groupby('neighborhood', as_index=False).agg({
    'violation_code': 'size',  
    'fine_amount': 'mean',
    'major_street': 'mean',  # using proportion of citations on major streets
    'amt_of_meters': 'first', 
    'issue_time': 'mean'
}).rename(columns={'violation_code': 'citation_count'})

# for categorical variables, get proportions 
# proportion by each month
month_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['month'], normalize='index')
month_props.columns = [f'month_{int(i)}' for i in range(month_props.shape[1])]
neighborhood_agg = neighborhood_agg.merge(month_props, left_on='neighborhood', right_index=True, how='left')

#  proportion by each day
day_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['day_of_week'], normalize='index')
day_props.columns = [f'day_{int(i)}' for i in range(day_props.shape[1])]
neighborhood_agg = neighborhood_agg.merge(day_props, left_on='neighborhood', right_index=True, how='left')

# proportion by each color
color_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['color'], normalize='index')
color_props.columns = [f'color_{int(i)}' for i in range(color_props.shape[1])]
neighborhood_agg = neighborhood_agg.merge(color_props, left_on='neighborhood', right_index=True, how='left')

# proportion by agency
agency_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['agency'], normalize='index')
agency_props.columns = [f'agency_{int(i)}' for i in range(agency_props.shape[1])]
neighborhood_agg = neighborhood_agg.merge(agency_props, left_on='neighborhood', right_index=True, how='left')

# proportion by violation type
top_violations = citations_2019['violation_code'].value_counts().head(8).index
violation_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['violation_code'], normalize='index')[top_violations]
violation_props.columns = [f'violation_{int(i)}' for i in range(violation_props.shape[1])]
neighborhood_agg = neighborhood_agg.merge(violation_props, left_on='neighborhood', right_index=True, how='left')

# all missing prroportions are 0
neighborhood_agg = neighborhood_agg.fillna(0)

print(f"Neighborhood-level dataset shape: {neighborhood_agg.shape}")
print(f"\nNeighborhoods included: {neighborhood_agg['neighborhood'].nunique()}")
print(f"\nSample of aggregated data:")
print(neighborhood_agg.head())
print(f"\nColumn names: {list(neighborhood_agg.columns)}")

# NEIGHBORHOOD-LEVEL NEGATIVE BINOMIAL MODEL

# repeat bc an error kept happening without this (?)
if 'neighborhood_agg' not in locals() or neighborhood_agg.shape[0] == 0:
    neighborhood_agg = citations_2019.groupby('neighborhood', as_index=False).agg({
        'violation_code': 'size',
        'fine_amount': 'mean',
        'major_street': 'mean',
        'amt_of_meters': 'first',
        'issue_time': 'mean'
    }).rename(columns={'violation_code': 'citation_count'})

    month_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['month'], normalize='index')
    month_props.columns = [f'month_{int(i)}' for i in range(month_props.shape[1])]
    neighborhood_agg = neighborhood_agg.merge(month_props, left_on='neighborhood', right_index=True, how='left')

    day_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['day_of_week'], normalize='index')
    day_props.columns = [f'day_{int(i)}' for i in range(day_props.shape[1])]
    neighborhood_agg = neighborhood_agg.merge(day_props, left_on='neighborhood', right_index=True, how='left')

    color_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['color'], normalize='index')
    color_props.columns = [f'color_{int(i)}' for i in range(color_props.shape[1])]
    neighborhood_agg = neighborhood_agg.merge(color_props, left_on='neighborhood', right_index=True, how='left')

    agency_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['agency'], normalize='index')
    agency_props.columns = [f'agency_{int(i)}' for i in range(agency_props.shape[1])]
    neighborhood_agg = neighborhood_agg.merge(agency_props, left_on='neighborhood', right_index=True, how='left')

    top_violations = citations_2019['violation_code'].value_counts().head(8).index
    violation_props = pd.crosstab(citations_2019['neighborhood'], citations_2019['violation_code'], normalize='index')[top_violations]
    violation_props.columns = [f'violation_{int(i)}' for i in range(violation_props.shape[1])]
    neighborhood_agg = neighborhood_agg.merge(violation_props, left_on='neighborhood', right_index=True, how='left')

    neighborhood_agg = neighborhood_agg.fillna(0)

# getting proportion column names 
prop_cols = [col for col in neighborhood_agg.columns 
             if col in neighborhood_agg.columns and col not in ['neighborhood', 'citation_count', 'fine_amount', 'major_street', 'amt_of_meters', 'issue_time']]

# create the formula for NB
formula = 'citation_count ~ fine_amount + major_street + amt_of_meters + issue_time + ' + ' + '.join(prop_cols)

print(f"Number of neighborhoods: {neighborhood_agg.shape[0]}")
print(f"Number of proportion predictors: {len(prop_cols)}")
print(f"Total predictors: {len(prop_cols) + 4}")

# fit NB model
nb_model = smf.glm(
    formula=formula,
    data=neighborhood_agg,
    family=sm.families.NegativeBinomial(link=sm.genmod.families.links.Log())
)
nb_results = nb_model.fit()


print("NEIGHBORHOOD-LEVEL NEGATIVE BINOMIAL MODEL")
print("-" * 80)
print(nb_results.summary())


print(f"Number of neighborhoods: {nb_results.nobs}")
print(f"Log-Likelihood: {nb_results.llf:.4f}")
print(f"AIC: {nb_results.aic:.4f}")
print(f"BIC: {nb_results.bic:.4f}")

# top predictors by vairable 
print("\n" + "=" * 80)
print("TOP 15 PREDICTORS (by absolute coefficient value)")
print("-" * 80)
coef_df = pd.DataFrame({
    'Variable': nb_results.params.index,
    'Coefficient': nb_results.params.values,
    'Std Error': nb_results.bse.values,
    'P-value': nb_results.pvalues.values
})
coef_df['Abs_Coef'] = coef_df['Coefficient'].abs()
coef_df = coef_df.sort_values('Abs_Coef', ascending=False)
print(coef_df[['Variable', 'Coefficient', 'P-value']].head(15))

# the new  predictions
neighborhood_agg['predicted_citation_count'] = nb_results.predict(neighborhood_agg)

print("\n" + "-" * 80)
print("NEIGHBORHOOD PREDICTIONS vs ACTUAL")
print("-" * 80)
print(neighborhood_agg[['neighborhood', 'citation_count', 'predicted_citation_count', 
                        'fine_amount', 'amt_of_meters', 'major_street']].head(11))

neighborhood_agg['residual'] = neighborhood_agg['citation_count'] - neighborhood_agg['predicted_citation_count']
neighborhood_agg.head()
