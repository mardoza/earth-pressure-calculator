import math

# ============================================================================
# MÉTODO DE MONONOBE-OKABE PARA EMPUJES SÍSMICOS
# ============================================================================


def mononobe_okabe_active(
    H: float,
    gamma: float,
    phi: float,
    c: float = 0.0,
    delta: float = 0.0,
    beta: float = 0.0,
    alpha: float = 90.0,
    kh: float = 0.0,
    kv: float = 0.0,
    q: float = 0.0,
    water_table: float = None
):
    """
    Teoría de Mononobe-Okabe para EMPUJE ACTIVO SÍSMICO.
    Sistema MKS: Metro, Kilogramo-fuerza, Segundo
    """

    phi_rad = math.radians(phi)
    delta_rad = math.radians(delta)
    beta_rad = math.radians(beta)
    alpha_rad = math.radians(alpha)
    gamma_water = 1000.0

    if (1 - kv) > 0:
        theta_rad = math.atan(kh / (1 - kv))
    else:
        theta_rad = math.atan(kh / 0.001)

    theta_deg = math.degrees(theta_rad)
    gamma_eff = gamma * (1 - kv)

    try:
        phi_theta = phi_rad + theta_rad
        alpha_delta = alpha_rad + delta_rad
        beta_theta = beta_rad - theta_rad

        numerador = math.cos(phi_theta) ** 2
        cos_alpha_delta = math.cos(alpha_delta)
        cos_beta_theta = math.cos(beta_theta)

        sin_term_num = math.sin(phi_theta + alpha_delta) * math.sin(phi_theta - beta_theta)
        sin_term_den = cos_alpha_delta * cos_beta_theta

        sin_term = sin_term_num / sin_term_den if sin_term_den > 0 else 0
        sqrt_term = math.sqrt(max(sin_term, 0.0))

        denominador = (
            cos_alpha_delta ** 2 *
            cos_beta_theta *
            (1 + sqrt_term) ** 2
        )

        KAE = numerador / denominador if denominador > 0 else math.tan(math.radians(45 - phi/2)) ** 2
    except Exception:
        KAE = math.tan(math.radians(45 - phi/2)) ** 2

    PAE_suelo = 0.5 * gamma_eff * H**2 * KAE
    PAE_sobrecarga = q * H * KAE
    PAE_cohesion = -2 * c * H * math.sqrt(KAE)
    PAE = PAE_suelo + PAE_sobrecarga + PAE_cohesion

    PAE_agua = 0.0
    if water_table is not None and water_table < H:
        h_water = H - water_table
        PAE_agua = 0.5 * gamma_water * h_water**2
        PAE += PAE_agua

    try:
        KA_sin_sismo = math.cos(alpha_rad - phi_rad) ** 2 / (
            math.cos(alpha_rad + delta_rad) ** 2 *
            math.cos(beta_rad) *
            (1 + math.sqrt(
                (math.sin(phi_rad + delta_rad) * math.sin(phi_rad - beta_rad)) /
                (math.cos(alpha_rad + delta_rad) * math.cos(beta_rad))
            )) ** 2
        )
    except Exception:
        KA_sin_sismo = math.tan(math.radians(45 - phi/2)) ** 2

    PA_sin_sismo = 0.5 * gamma * H**2 * KA_sin_sismo + q * H * KA_sin_sismo - 2 * c * H * math.sqrt(KA_sin_sismo)
    delta_PAE = PAE - PA_sin_sismo

    return {
        "metodo": "MONONOBE-OKABE",
        "tipo": "ACTIVO SÍSMICO",
        "KAE": KAE,
        "theta_rad": theta_rad,
        "theta_deg": theta_deg,
        "gamma_eff": gamma_eff,
        "PAE": PAE,
        "PAE_suelo": PAE_suelo,
        "PAE_sobrecarga": PAE_sobrecarga,
        "PAE_cohesion": PAE_cohesion,
        "PAE_agua": PAE_agua,
        "PA_sin_sismo": PA_sin_sismo,
        "delta_PAE": delta_PAE,
        "z_PAE": H / 3.0,
        "z_delta_PAE": H / 2.0,
        "H": H,
        "kh": kh,
        "kv": kv
    }


def mononobe_okabe_passive(
    H: float,
    gamma: float,
    phi: float,
    c: float = 0.0,
    delta: float = 0.0,
    beta: float = 0.0,
    alpha: float = 90.0,
    kh: float = 0.0,
    kv: float = 0.0,
    q: float = 0.0,
    water_table: float = None
):
    """Teoría de Mononobe-Okabe para EMPUJE PASIVO SÍSMICO."""

    phi_rad = math.radians(phi)
    delta_rad = math.radians(delta)
    beta_rad = math.radians(beta)
    alpha_rad = math.radians(alpha)
    gamma_water = 1000.0

    if (1 - kv) > 0:
        theta_rad = math.atan(kh / (1 - kv))
    else:
        theta_rad = math.atan(kh / 0.001)

    theta_deg = math.degrees(theta_rad)
    gamma_eff = gamma * (1 - kv)

    try:
        phi_theta = phi_rad + theta_rad
        alpha_delta = alpha_rad - delta_rad
        beta_theta = beta_rad + theta_rad

        numerador = math.cos(phi_theta) ** 2
        cos_alpha_delta = math.cos(alpha_delta)
        cos_beta_theta = math.cos(beta_theta)

        sin_term_num = math.sin(phi_theta - alpha_delta) * math.sin(phi_theta + beta_theta)
        sin_term_den = cos_alpha_delta * cos_beta_theta

        sin_term = sin_term_num / sin_term_den if sin_term_den > 0 else 0
        sqrt_term = math.sqrt(max(sin_term, 0.0))

        denominador = (
            cos_alpha_delta ** 2 *
            cos_beta_theta *
            (1 - sqrt_term) ** 2
        )

        KPE = numerador / denominador if denominador > 0 else math.tan(math.radians(45 + phi/2)) ** 2
    except Exception:
        KPE = math.tan(math.radians(45 + phi/2)) ** 2

    PPE_suelo = 0.5 * gamma_eff * H**2 * KPE
    PPE_sobrecarga = q * H * KPE
    PPE_cohesion = 2 * c * H * math.sqrt(KPE)
    PPE = PPE_suelo + PPE_sobrecarga + PPE_cohesion

    PPE_agua = 0.0
    if water_table is not None and water_table < H:
        h_water = H - water_table
        PPE_agua = 0.5 * gamma_water * h_water**2
        PPE += PPE_agua

    try:
        KP_sin_sismo = math.cos(alpha_rad - phi_rad) ** 2 / (
            math.cos(alpha_rad - delta_rad) ** 2 *
            math.cos(beta_rad) *
            (1 - math.sqrt(
                (math.sin(phi_rad - delta_rad) * math.sin(phi_rad + beta_rad)) /
                (math.cos(alpha_rad - delta_rad) * math.cos(beta_rad))
            )) ** 2
        )
    except Exception:
        KP_sin_sismo = math.tan(math.radians(45 + phi/2)) ** 2

    PP_sin_sismo = 0.5 * gamma * H**2 * KP_sin_sismo + q * H * KP_sin_sismo + 2 * c * H * math.sqrt(KP_sin_sismo)
    delta_PPE = PP_sin_sismo - PPE

    return {
        "metodo": "MONONOBE-OKABE",
        "tipo": "PASIVO SÍSMICO",
        "KPE": KPE,
        "theta_rad": theta_rad,
        "theta_deg": theta_deg,
        "gamma_eff": gamma_eff,
        "PPE": PPE,
        "PPE_suelo": PPE_suelo,
        "PPE_sobrecarga": PPE_sobrecarga,
        "PPE_cohesion": PPE_cohesion,
        "PPE_agua": PPE_agua,
        "PP_sin_sismo": PP_sin_sismo,
        "delta_PPE": delta_PPE,
        "z_PPE": H / 3.0,
        "z_delta_PPE": H / 2.0,
        "H": H,
        "kh": kh,
        "kv": kv
    }


def rankine_active_passive(
    H: float,
    gamma: float,
    phi: float,
    c: float = 0.0,
    beta: float = 0.0,
    q: float = 0.0,
    water_table: float = None
):
    """Teoría de Rankine (sin sismo)"""

    phi_rad = math.radians(phi)
    beta_rad = math.radians(beta)
    gamma_water = 1000.0

    if beta == 0:
        Ka = math.tan(math.radians(45 - phi/2)) ** 2
        Kp = math.tan(math.radians(45 + phi/2)) ** 2
    else:
        Ka = (math.cos(beta_rad) - math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2)) / \
             (math.cos(beta_rad) + math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2))
        Kp = (math.cos(beta_rad) + math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2)) / \
             (math.cos(beta_rad) - math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2))

    Pa_suelo = 0.5 * gamma * H**2 * Ka
    Pp_suelo = 0.5 * gamma * H**2 * Kp
    Pa_sobrecarga = q * H * Ka
    Pp_sobrecarga = q * H * Kp
    Pa_cohesion = -2 * c * H * math.sqrt(Ka)
    Pp_cohesion = 2 * c * H * math.sqrt(Kp)

    Pa = Pa_suelo + Pa_sobrecarga + Pa_cohesion
    Pp = Pp_suelo + Pp_sobrecarga + Pp_cohesion

    Pa_agua = 0.0
    Pp_agua = 0.0
    if water_table is not None and water_table < H:
        h_water = H - water_table
        Pa_agua = 0.5 * gamma_water * h_water**2
        Pp_agua = 0.5 * gamma_water * h_water**2
        Pa += Pa_agua
        Pp += Pp_agua

    return {
        "metodo": "RANKINE",
        "Ka": Ka,
        "Kp": Kp,
        "Pa": Pa,
        "Pp": Pp,
        "Pa_suelo": Pa_suelo,
        "Pa_sobrecarga": Pa_sobrecarga,
        "Pa_cohesion": Pa_cohesion,
        "Pa_agua": Pa_agua,
        "Pp_suelo": Pp_suelo,
        "Pp_sobrecarga": Pp_sobrecarga,
        "Pp_cohesion": Pp_cohesion,
        "Pp_agua": Pp_agua,
        "sigma_active_base": gamma * H * Ka,
        "sigma_passive_base": gamma * H * Kp,
        "z_Pa": H / 3.0,
        "z_Pp": H / 3.0,
        "H": H
    }


def coulomb_active_passive(
    H: float,
    gamma: float,
    phi: float,
    c: float = 0.0,
    delta: float = 0.0,
    beta: float = 0.0,
    alpha: float = 90.0,
    q: float = 0.0,
    water_table: float = None
):
    """Teoría de Coulomb (sin sismo)"""

    phi_rad = math.radians(phi)
    delta_rad = math.radians(delta)
    beta_rad = math.radians(beta)
    alpha_rad = math.radians(alpha)
    gamma_water = 1000.0

    try:
        KA = math.cos(alpha_rad - phi_rad) ** 2 / (
            math.cos(alpha_rad + delta_rad) ** 2 *
            math.cos(beta_rad) *
            (1 + math.sqrt(
                (math.sin(phi_rad + delta_rad) * math.sin(phi_rad - beta_rad)) /
                (math.cos(alpha_rad + delta_rad) * math.cos(beta_rad))
            )) ** 2
        )
    except Exception:
        KA = math.tan(math.radians(45 - phi/2)) ** 2

    try:
        KP = math.cos(alpha_rad - phi_rad) ** 2 / (
            math.cos(alpha_rad - delta_rad) ** 2 *
            math.cos(beta_rad) *
            (1 - math.sqrt(
                (math.sin(phi_rad - delta_rad) * math.sin(phi_rad + beta_rad)) /
                (math.cos(alpha_rad - delta_rad) * math.cos(beta_rad))
            )) ** 2
        )
    except Exception:
        KP = math.tan(math.radians(45 + phi/2)) ** 2

    Pa_suelo = 0.5 * gamma * H**2 * KA
    Pp_suelo = 0.5 * gamma * H**2 * KP
    Pa_sobrecarga = q * H * KA
    Pp_sobrecarga = q * H * KP
    Pa_cohesion = -2 * c * H * math.sqrt(KA)
    Pp_cohesion = 2 * c * H * math.sqrt(KP)

    Pa = Pa_suelo + Pa_sobrecarga + Pa_cohesion
    Pp = Pp_suelo + Pp_sobrecarga + Pp_cohesion

    Pa_agua = 0.0
    Pp_agua = 0.0
    if water_table is not None and water_table < H:
        h_water = H - water_table
        Pa_agua = 0.5 * gamma_water * h_water**2
        Pp_agua = 0.5 * gamma_water * h_water**2
        Pa += Pa_agua
        Pp += Pp_agua

    return {
        "metodo": "COULOMB",
        "KA": KA,
        "KP": KP,
        "Pa": Pa,
        "Pp": Pp,
        "Pa_suelo": Pa_suelo,
        "Pa_sobrecarga": Pa_sobrecarga,
        "Pa_cohesion": Pa_cohesion,
        "Pa_agua": Pa_agua,
        "Pp_suelo": Pp_suelo,
        "Pp_sobrecarga": Pp_sobrecarga,
        "Pp_cohesion": Pp_cohesion,
        "Pp_agua": Pp_agua,
        "sigma_active_base": gamma * H * KA,
        "sigma_passive_base": gamma * H * KP,
        "z_Pa": H / 3.0,
        "z_Pp": H / 3.0,
        "H": H
    }


def analizar_resultados_completo(rankine, coulomb, mononobe_active, mononobe_passive):
    """Análisis comparativo de todos los métodos"""

    Pa_rankine = rankine["Pa"]
    Pa_coulomb = coulomb["Pa"]
    Pa_mononobe = mononobe_active["PAE"]

    Pp_rankine = rankine["Pp"]
    Pp_coulomb = coulomb["Pp"]
    Pp_mononobe = mononobe_passive["PPE"]

    Pa_max = max(Pa_rankine, Pa_coulomb, Pa_mononobe)
    if Pa_max == Pa_rankine:
        Pa_critico_metodo = "RANKINE"
    elif Pa_max == Pa_coulomb:
        Pa_critico_metodo = "COULOMB"
    else:
        Pa_critico_metodo = "MONONOBE-OKABE"

    Pp_min = min(Pp_rankine, Pp_coulomb, Pp_mononobe)
    if Pp_min == Pp_rankine:
        Pp_critico_metodo = "RANKINE"
    elif Pp_min == Pp_coulomb:
        Pp_critico_metodo = "COULOMB"
    else:
        Pp_critico_metodo = "MONONOBE-OKABE"

    return {
        "Pa_rankine": Pa_rankine,
        "Pa_coulomb": Pa_coulomb,
        "Pa_mononobe": Pa_mononobe,
        "Pa_max": Pa_max,
        "Pa_critico_metodo": Pa_critico_metodo,
        "Pp_rankine": Pp_rankine,
        "Pp_coulomb": Pp_coulomb,
        "Pp_mononobe": Pp_mononobe,
        "Pp_min": Pp_min,
        "Pp_critico_metodo": Pp_critico_metodo,
        "FS_critico": Pp_min / Pa_max if Pa_max > 0 else 0,
        "delta_Pa_mononobe": mononobe_active["delta_PAE"],
        "delta_Pp_mononobe": mononobe_passive["delta_PPE"]
    }


def mostrar_tabla_comparativa_completa(rankine, coulomb, mononobe_a, mononobe_p, analisis):
    print("\n" + "="*100)
    print("TABLA COMPARATIVA: RANKINE vs COULOMB vs MONONOBE-OKABE")
    print("="*100)
    print()
    print(f"{'PARÁMETRO':<45} {'RANKINE':>15} {'COULOMB':>15} {'MONONOBE-OKABE':>15}")
    print("-" * 100)
    print(f"{'Coeficiente Ka / KAE':<45} {rankine['Ka']:>15.4f} {coulomb['KA']:>15.4f} {mononobe_a['KAE']:>15.4f}")
    print(f"{'Coeficiente Kp / KPE':<45} {rankine['Kp']:>15.4f} {coulomb['KP']:>15.4f} {mononobe_p['KPE']:>15.4f}")
    print()
    print(f"{'EMPUJE ACTIVO Pa [kgf/m]':<45} {rankine['Pa']:>15.2f} {coulomb['Pa']:>15.2f} {mononobe_a['PAE']:>15.2f}")
    print(f"{'  → Por suelo':<45} {rankine['Pa_suelo']:>15.2f} {coulomb['Pa_suelo']:>15.2f} {mononobe_a['PAE_suelo']:>15.2f}")
    print(f"{'  → Por sobrecarga':<45} {rankine['Pa_sobrecarga']:>15.2f} {coulomb['Pa_sobrecarga']:>15.2f} {mononobe_a['PAE_sobrecarga']:>15.2f}")
    print(f"{'  → Por cohesión':<45} {rankine['Pa_cohesion']:>15.2f} {coulomb['Pa_cohesion']:>15.2f} {mononobe_a['PAE_cohesion']:>15.2f}")
    print(f"{'  → Por agua':<45} {rankine['Pa_agua']:>15.2f} {coulomb['Pa_agua']:>15.2f} {mononobe_a['PAE_agua']:>15.2f}")
    print()
    print(f"{'EMPUJE PASIVO Pp [kgf/m]':<45} {rankine['Pp']:>15.2f} {coulomb['Pp']:>15.2f} {mononobe_p['PPE']:>15.2f}")
    print(f"{'  → Por suelo':<45} {rankine['Pp_suelo']:>15.2f} {coulomb['Pp_suelo']:>15.2f} {mononobe_p['PPE_suelo']:>15.2f}")
    print(f"{'  → Por sobrecarga':<45} {rankine['Pp_sobrecarga']:>15.2f} {coulomb['Pp_sobrecarga']:>15.2f} {mononobe_p['PPE_sobrecarga']:>15.2f}")
    print(f"{'  → Por cohesión':<45} {rankine['Pp_cohesion']:>15.2f} {coulomb['Pp_cohesion']:>15.2f} {mononobe_p['PPE_cohesion']:>15.2f}")
    print(f"{'  → Por agua':<45} {rankine['Pp_agua']:>15.2f} {coulomb['Pp_agua']:>15.2f} {mononobe_p['PPE_agua']:>15.2f}")
    print()
    print(f"{'Incremento sísmico ΔPa [kgf/m]':<45} {'—':>15} {'—':>15} {mononobe_a['delta_PAE']:>15.2f}")
    print(f"{'Reducción sísmica ΔPp [kgf/m]':<45} {'—':>15} {'—':>15} {mononobe_p['delta_PPE']:>15.2f}")
    print()


def mostrar_analisis_desfavorable_completo(analisis, mononobe_a, mononobe_p, kh, kv):
    print("\n" + "="*100)
    print("ANÁLISIS DE CASO DESFAVORABLE (CRÍTICO) - RECOMENDACIÓN PARA DISEÑO")
    print("="*100)
    print()

    print("PARÁMETROS SÍSMICOS UTILIZADOS:")
    print("-" * 100)
    print(f"  Aceleración horizontal (kh):          {kh:.3f} g ({kh*9.81:.2f} m/s²)")
    print(f"  Aceleración vertical (kv):            {kv:.3f} g ({kv*9.81:.2f} m/s²)")
    print(f"  Ángulo de fricción sísmica (θ):       {mononobe_a['theta_deg']:.2f}°")
    print(f"  Peso unitario efectivo sísmico:       {mononobe_a['gamma_eff']:.2f} kgf/m³")
    print()

    print("EMPUJE ACTIVO (Pa) - CASO MÁS CRÍTICO:")
    print("-" * 100)
    print(f"  Rankine:                             {analisis['Pa_rankine']:>12.2f} kgf/m")
    print(f"  Coulomb:                             {analisis['Pa_coulomb']:>12.2f} kgf/m")
    print(f"  Mononobe-Okabe:                      {analisis['Pa_mononobe']:>12.2f} kgf/m")
    print()
    print(f"  ⚠️  VALOR CRÍTICO (MÁXIMO):           {analisis['Pa_critico_metodo']} = {analisis['Pa_max']:.2f} kgf/m")
    print()

    if analisis['Pa_critico_metodo'] == "MONONOBE-OKABE":
        print("  ✅ RECOMENDACIÓN: USAR MONONOBE-OKABE PARA EMPUJE ACTIVO")
        print("     Razón: considera el efecto dinámico completo del sismo.")
        print(f"     ΔPa = {analisis['delta_Pa_mononobe']:.2f} kgf/m")
    elif analisis['Pa_critico_metodo'] == "COULOMB":
        print("  ✅ RECOMENDACIÓN: USAR COULOMB PARA EMPUJE ACTIVO")
        print("     Razón: en este caso considera mejor la fricción muro-suelo.")
    else:
        print("  ✅ RECOMENDACIÓN: USAR RANKINE PARA EMPUJE ACTIVO")

    print()
    print("EMPUJE PASIVO (Pp) - CASO MÁS CRÍTICO:")
    print("-" * 100)
    print(f"  Rankine:                             {analisis['Pp_rankine']:>12.2f} kgf/m")
    print(f"  Coulomb:                             {analisis['Pp_coulomb']:>12.2f} kgf/m")
    print(f"  Mononobe-Okabe:                      {analisis['Pp_mononobe']:>12.2f} kgf/m")
    print()
    print(f"  ⚠️  VALOR CRÍTICO (MÍNIMO):           {analisis['Pp_critico_metodo']} = {analisis['Pp_min']:.2f} kgf/m")
    print()

    if analisis['Pp_critico_metodo'] == "MONONOBE-OKABE":
        print("  ✅ RECOMENDACIÓN: USAR MONONOBE-OKABE PARA EMPUJE PASIVO")
        print(f"     Razón: se reduce la resistencia pasiva por sismo; ΔPp = {analisis['delta_Pp_mononobe']:.2f} kgf/m")
    elif analisis['Pp_critico_metodo'] == "COULOMB":
        print("  ✅ RECOMENDACIÓN: USAR COULOMB PARA EMPUJE PASIVO")
    else:
        print("  ✅ RECOMENDACIÓN: USAR RANKINE PARA EMPUJE PASIVO")

    print()
    print("FACTOR DE SEGURIDAD CRÍTICO:")
    print("-" * 100)
    print(f"  FS (Pp/Pa) con Rankine:              {analisis['Pp_rankine'] / analisis['Pa_rankine'] if analisis['Pa_rankine'] > 0 else 0:>12.2f}")
    print(f"  FS (Pp/Pa) con Coulomb:              {analisis['Pp_coulomb'] / analisis['Pa_coulomb'] if analisis['Pa_coulomb'] > 0 else 0:>12.2f}")
    print(f"  FS (Pp/Pa) con Mononobe:             {analisis['Pp_mononobe'] / analisis['Pa_mononobe'] if analisis['Pa_mononobe'] > 0 else 0:>12.2f}")
    print(f"  ⚠️  FS CRÍTICO (MÍNIMO):              {analisis['FS_critico']:>12.2f}")
    print()

    if analisis['FS_critico'] < 1.0:
        print("  ❌ CRÍTICO: Factor de seguridad < 1.0")
    elif analisis['FS_critico'] < 1.5:
        print("  ⚠️  ADVERTENCIA: Factor de seguridad bajo")
    else:
        print("  ✅ ACEPTABLE: Factor de seguridad adecuado")

    print()


def mostrar_explicacion_mononobe():
    print("\n" + "="*100)
    print("TEORÍA DE MONONOBE-OKABE - EXPLICACIÓN TÉCNICA")
    print("="*100)
    print()
    print("¿QUÉ ES MONONOBE-OKABE?")
    print("Es una extensión de la teoría de Coulomb que incorpora el efecto sísmico mediante:")
    print("- ángulo de fricción sísmica θ = atan(kh / (1 - kv))")
    print("- peso unitario efectivo γ' = γ(1 - kv)")
    print("- coeficientes dinámmicos KAE y KPE")
    print()
    print("RESULTADOS TÍPICOS:")
    print("- Pa aumenta por sismo (KAE > Ka)")
    print("- Pp disminuye por sismo (KPE < Kp)")
    print("- Es el método recomendado para muros de contención con cargas sísmicas")
    print()


def main():
    print("\n" + "="*100)
    print("CALCULADORA DE EMPUJES: RANKINE vs COULOMB vs MONONOBE-OKABE")
    print("SISTEMA MKS (Metro, Kilogramo-fuerza, Segundo)")
    print("="*100 + "\n")

    print("DATOS DEL MURO Y SUELO:")
    print("-" * 100)
    H = float(input("Altura total del muro H [m]: "))
    gamma = float(input("Peso unitario del suelo γ [kgf/m³]: "))
    phi = float(input("Ángulo de fricción interna φ [°]: "))
    c = float(input("Cohesión c [kgf/m²] (0 si no existe): ") or 0)
    delta = float(input("Ángulo de fricción muro-suelo δ [°] (0 si no hay): ") or 0)
    beta = float(input("Inclinación del relleno β [°] (0 si es horizontal): ") or 0)
    alpha = float(input("Inclinación del muro α [°] (90 si es vertical): ") or 90)
    q = float(input("Sobrecarga superficial q [kgf/m²] (0 si no hay): ") or 0)

    print("\nPARÁMETROS SÍSMICOS:")
    print("-" * 100)
    kh = float(input("Aceleración sísmica horizontal kh [g]: "))
    kv = float(input("Aceleración sísmica vertical kv [g] (0 si no hay): ") or 0)

    water_table_input = input("\n¿Hay nivel freático? (s/n): ").lower()
    water_table = None
    if water_table_input == 's':
        water_table = float(input("Profundidad del nivel freático desde la base [m]: "))

    print("\n" + "="*100)
    print("PROCESANDO CÁLCULOS...")
    print("="*100)

    rankine = rankine_active_passive(H, gamma, phi, c, beta, q, water_table)
    coulomb = coulomb_active_passive(H, gamma, phi, c, delta, beta, alpha, q, water_table)
    mononobe_a = mononobe_okabe_active(H, gamma, phi, c, delta, beta, alpha, kh, kv, q, water_table)
    mononobe_p = mononobe_okabe_passive(H, gamma, phi, c, delta, beta, alpha, kh, kv, q, water_table)

    analisis = analizar_resultados_completo(rankine, coulomb, mononobe_a, mononobe_p)
    mostrar_tabla_comparativa_completa(rankine, coulomb, mononobe_a, mononobe_p, analisis)
    mostrar_analisis_desfavorable_completo(analisis, mononobe_a, mononobe_p, kh, kv)
    mostrar_explicacion_mononobe()

    print("\n" + "="*100)
    print("NOTAS IMPORTANTES:")
    print("="*100)
    print("• Sistema MKS: distancias [m], fuerzas [kgf], presiones [kgf/m²]")
    print("• 1 kgf ≈ 9.81 N; 1 kgf/m² ≈ 9.81 Pa")
    print("• Para DISEÑO SÍSMICO, siempre usar los valores MÁS CRÍTICOS (MÁXIMO Pa, MÍNIMO Pp)")
    print("• Mononobe-Okabe es el método recomendado para análisis sísmicos")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
