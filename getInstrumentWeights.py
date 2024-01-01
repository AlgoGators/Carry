# In order to successfully weight each future asset, we must first split our futures assets into different asset classes

INSTRUMENT_LIST = ['6A_Data', '6B_Data', '6C_Data', '6E_Data', '6J_Data', '6M_Data', '6N_Data', '6S_Data', 'AFB_Data', 'AWM_Data', 'BAX_Data', 'BRN_Data', 'BTC_Data', 'CC_Data', 'CGB_Data', 'CL_Data', 'CT_Data', 'DC_Data', 'DX_Data', 'EMD_Data', 'ES_Data', 'ETH_Data', 'EUA_Data', 'FBTP_Data', 'FCE_Data', 'FDAX_Data', 'FESX_Data', 'FGBL_Data', 'FGBM_Data', 'FGBS_Data', 'FGBX_Data', 'FOAT_Data', 'FSMI_Data', 'FTDX_Data', 'GAS_Data', 'GC_Data', 'GD_Data', 'GE_Data', 'GF_Data', 'GWM_Data', 'HE_Data', 'HG_Data', 'HO_Data', 'HSI_Data', 'HTW_Data', 'KC_Data', 'KE_Data', 'KOS_Data', 'LBS_Data', 'LCC_Data', 'LES_Data', 'LEU_Data', 'LE_Data', 'LFT_Data', 'LLG_Data', 'LRC_Data', 'LSS_Data', 'LSU_Data', 'LWB_Data', 'M2K_Data', 'MBT_Data', 'MES_Data', 'MET_Data', 'MHI_Data', 'MNQ_Data', 'MWE_Data', 'MYM_Data', 'NG_Data', 'NIY_Data', 'NKD_Data', 'NQ_Data', 'OJ_Data', 'PA_Data', 'PL_Data', 'RB_Data', 'RS_Data', 'RTY_Data', 'SB_Data', 'SCN_Data', 'SI_Data', 'SJB_Data', 'SNK_Data', 'SO3_Data', 'SR3_Data', 'SSG_Data', 'SXF_Data', 'TN_Data', 'UB_Data', 'VX_Data', 'WBS_Data', 'YAP_Data', 'YG_Data', 'YIB_Data', 'YIR_Data', 'YI_Data', 'YM_Data', 'YXT_Data', 'YYT_Data', 'ZB_Data', 'ZC_Data', 'ZF_Data', 'ZL_Data', 'ZM_Data', 'ZN_Data', 'ZO_Data', 'ZQ_Data', 'ZR_Data', 'ZS_Data', 'ZT_Data', 'ZW_Data']


asset_class_groupings = {
    'Currency Futures': ['6A_Data', '6B_Data', '6C_Data', '6E_Data', '6J_Data', '6M_Data', '6N_Data', '6S_Data'],
    'Agricultural Futures': ['AFB_Data', 'AWM_Data', 'CC_Data', 'CGB_Data', 'CT_Data', 'CFE_Data', 'FESX_Data', 'FOAT_Data', 'FGBX_Data', 'FGBL_Data', 'FGBM_Data', 'FGBS_Data', 'KC_Data', 'OJ_Data', 'PA_Data', 'SB_Data'],
    'Energy Futures': ['BRN_Data', 'CL_Data', 'HO_Data', 'NG_Data', 'RB_Data'],
    'Equity and Index Futures': ['EMD_Data', 'ES_Data', 'FDAX_Data', 'FCE_Data', 'M2K_Data', 'MES_Data', 'MNQ_Data', 'MYM_Data'],
    'Interest Rate Futures': ['FBTP_Data', 'TN_Data', 'UB_Data', 'ZB_Data', 'ZF_Data', 'ZN_Data', 'ZT_Data'],
    'Metals and Other Futures': ['GC_Data', 'HG_Data', 'PL_Data', 'SI_Data', 'BTC_Data', 'ETH_Data']
}

# Number of asset classes
num_asset_classes = len(asset_class_groupings)

# Initialize weights dictionary
weights = {}

# Initialize weights dictionary
weights = {}

# Calculate weights for each asset class
for asset_class, assets in asset_class_groupings.items():
    num_assets_in_class = len(assets)
    weight_per_asset = 1 / num_assets_in_class

    # Assign weight to each asset in the class
    for asset in assets:
        weights[asset] = weight_per_asset

# Display the weights
print(weights)

