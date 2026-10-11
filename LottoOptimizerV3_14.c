/* Lotto Optimizer V3.14 — el 13 con la pantalla dentro del exe. */
#define WIN32_LEAN_AND_MEAN
#define _CRT_SECURE_NO_WARNINGS
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <winhttp.h>
#include <shellapi.h>
#include <commdlg.h>
#include <ctype.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

#define MAXN 64
#define UNIVERSO_DEF 50000
#define MAX_SORTEOS 20000000
#define LOGN 80

typedef struct { int *idx; int n, cap; } Lista;
typedef struct { uint64_t mask; int min_a, max_a; } Grupo;
typedef struct {
    int activo;
    int suma_min, suma_max, pares_min, pares_max, bajos_min, bajos_max;
    int dist_min, dist_max, seguidos_max, decena_max, term_max;
    int incluir[MAXN];
    int nincluir;
} Filtros;
typedef struct {
    int v, k, t, m, universo, cantidad, ciclos, nbase, ngrupos;
    double porc;
    int modo_p, usar_record;
    int base[MAXN];
    Grupo grupos[32];
    Filtros filtros;
    char modo[16];
    char url[600];
} Job;
typedef struct {
    int v, k, t, m, filtro_v, universo_n, tiene_mapa, nap, cap, mejor_n, cubiertos, ngrupos, exacto;
    int mapa[MAXN];
    uint64_t *universo, *ap, *mejor;
    int *conteos;
    unsigned *visto, sello;
    Lista por[MAXN + 1];
    double temp, mejor_cob, cob_vista;
    uint64_t total_sorteos;
    unsigned long long ciclos;
    Grupo grupos[32];
    Filtros filtros;
} Opt;
typedef struct { int v, k, t, m; const char *url; } Reducida;
typedef struct { int n[MAXN]; int k; } Fila;

static const Reducida REDUCIDAS[] = {
#include "reducidas.inc"
};
static const int NRED = (int)(sizeof REDUCIDAS / sizeof REDUCIDAS[0]);

static uint64_t g_rng = 0x9E3779B97F4A7C15ull;
static CRITICAL_SECTION g_cs;
static volatile LONG g_parar, g_salir, g_ocupado;
static char g_ahora[40] = "Listo";
static char g_linea[240] = "Esperando. Calcular genera las apuestas.";
static char g_cob[32] = "";
static char g_nota[80] = "";
static int g_exacto;
static char g_log[LOGN][240];
static int g_nlog, g_apuestas, g_v, g_k, g_t;
static uint64_t *g_bets;
static int g_nbets;
static unsigned long long g_tope;

static uint64_t rnd64(void) {
    uint64_t x = g_rng;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    g_rng = x;
    return x * 0x2545F4914F6CDD1Dull;
}

static void filtros_init(Filtros *f) {
    memset(f, 0, sizeof *f);
    f->suma_min = f->suma_max = f->pares_min = f->pares_max = INT_MIN;
    f->bajos_min = f->bajos_max = f->dist_min = f->dist_max = INT_MIN;
    f->seguidos_max = f->decena_max = f->term_max = INT_MIN;
}

static void poner_ahora(const char *linea) {
    char t[240];
    int i;
    const char *a = "Ahora";
    for (i = 0; linea[i] && i < 239; i++) t[i] = (char)tolower((unsigned char)linea[i]);
    t[i] = 0;
    if (strstr(t, "error")) a = "Error";
    else if (strstr(t, "progreso") || strstr(t, "generando")) a = "Generando";
    else if (strstr(t, "ciclo") || strstr(t, "optimiz")) a = "Optimizando";
    else if (strstr(t, "incorporando") || strstr(t, "descargando")) a = "Cargando";
    else if (strstr(t, "detenid") || strstr(t, "parar")) a = "Parado";
    else if (strstr(t, "archivo") || strstr(t, "guardad")) a = "Guardado";
    else if (strchr(t, '%')) a = "Cobertura";
    snprintf(g_ahora, sizeof g_ahora, "%s", a);
}

static void anotar(const char *texto) {
    char copia[8192];
    char *p;
    snprintf(copia, sizeof copia, "%s", texto);
    EnterCriticalSection(&g_cs);
    p = copia;
    while (*p) {
        char *nl = strpbrk(p, "\r\n");
        if (nl) *nl = 0;
        if (*p) {
            if (g_nlog == LOGN) {
                memmove(g_log, g_log + 1, (LOGN - 1) * 240);
                g_nlog = LOGN - 1;
            }
            snprintf(g_log[g_nlog], 240, "%s", p);
            snprintf(g_linea, sizeof g_linea, "%s", p);
            poner_ahora(p);
            g_nlog++;
        }
        if (!nl) break;
        p = nl + 1;
        if (*p == '\n' || *p == '\r') p++;
    }
    LeaveCriticalSection(&g_cs);
}

static const char *titulo_accion(const char *nombre) {
    if (!strcmp(nombre, "calcular")) return "Calcular";
    if (!strcmp(nombre, "parar")) return "Parar";
    if (!strcmp(nombre, "escrutar")) return "Escrutar";
    if (!strcmp(nombre, "garantias")) return "Garantías";
    if (!strcmp(nombre, "analizar")) return "Análisis";
    if (!strcmp(nombre, "validar")) return "Validar";
    if (!strcmp(nombre, "estadisticas")) return "Estadísticas";
    if (!strcmp(nombre, "cargar")) return "Cargar";
    if (!strcmp(nombre, "guardar")) return "Guardar";
    if (!strcmp(nombre, "usar")) return "Usar récord";
    if (!strcmp(nombre, "mejorar")) return "Mejorar récord";
    return nombre;
}

static void raya(const char *nombre) {
    char marca[80];
    snprintf(marca, sizeof marca, "-------- %s --------", titulo_accion(nombre));
    EnterCriticalSection(&g_cs);
    if (g_nlog > 0 && strcmp(g_log[g_nlog - 1], marca) != 0) {
        if (g_nlog == LOGN) {
            memmove(g_log, g_log + 1, (LOGN - 1) * 240);
            g_nlog = LOGN - 1;
        }
        snprintf(g_log[g_nlog], 240, "%s", marca);
        g_nlog++;
    }
    LeaveCriticalSection(&g_cs);
}

static void limpiar_log(void) {
    EnterCriticalSection(&g_cs);
    g_nlog = 0;
    LeaveCriticalSection(&g_cs);
}

static void progreso(const char *linea, double cob) {
    EnterCriticalSection(&g_cs);
    snprintf(g_linea, sizeof g_linea, "%s", linea);
    poner_ahora(linea);
    if (cob >= 0) snprintf(g_cob, sizeof g_cob, "%.4f%%", cob);
    LeaveCriticalSection(&g_cs);
}

static const char *salta_string(const char *p) {
    if (*p != '"') return p;
    p++;
    while (*p && *p != '"') {
        if (*p == '\\' && p[1]) p++;
        p++;
    }
    if (*p == '"') p++;
    return p;
}

static const char *salta_ws(const char *p) {
    while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r') p++;
    return p;
}

static const char *json_valor(const char *obj, const char *end, const char *key) {
    size_t klen = strlen(key);
    const char *p = obj;
    if (!obj) return NULL;
    if (!end) end = obj + strlen(obj);
    while (p < end && *p) {
        if (*p != '"') { p++; continue; }
        if ((size_t)(end - (p + 1)) >= klen + 1 && strncmp(p + 1, key, klen) == 0 && p[1 + klen] == '"') {
            const char *v = salta_ws(p + klen + 2);
            if (v < end && *v == ':') return salta_ws(v + 1);
        }
        p = salta_string(p);
    }
    return NULL;
}

static int objeto_fin(const char *v, const char **fin) {
    int d = 0;
    const char *p;
    if (!v || (*v != '{' && *v != '[')) return 0;
    p = v;
    do {
        if (*p == '"') { p = salta_string(p); continue; }
        if (*p == '{' || *p == '[') d++;
        else if (*p == '}' || *p == ']') d--;
        if (*p) p++;
    } while (*p && d);
    *fin = p;
    return 1;
}

static int json_str(const char *obj, const char *end, const char *key, char *dst, int cap) {
    const char *v = json_valor(obj, end, key);
    int n = 0;
    if (dst && cap) dst[0] = 0;
    if (!v || *v != '"') return 0;
    v++;
    while (*v && *v != '"' && n < cap - 1) {
        if (*v == '\\' && v[1]) {
            v++;
            if (*v == 'n') dst[n++] = '\n';
            else if (*v == 'r') dst[n++] = '\r';
            else if (*v == 't') dst[n++] = '\t';
            else dst[n++] = *v;
            v++;
        } else dst[n++] = *v++;
    }
    dst[n] = 0;
    return 1;
}

static int json_bool(const char *obj, const char *end, const char *key) {
    const char *v = json_valor(obj, end, key);
    return v && strncmp(v, "true", 4) == 0;
}

static int json_ints(const char *obj, const char *end, const char *key, int *out, int max) {
    const char *v = json_valor(obj, end, key);
    int n = 0;
    if (!v || *v != '[') return 0;
    v++;
    while (*v && *v != ']' && n < max) {
        while (*v == ' ' || *v == ',' || *v == '\n' || *v == '\r') v++;
        if (*v == ']' || !*v) break;
        out[n++] = atoi(v);
        while (*v && *v != ',' && *v != ']') v++;
    }
    return n;
}

static int leer_int(const char *obj, const char *end, const char *key, int *out, int obligatorio) {
    const char *v = json_valor(obj, end, key);
    char *e = NULL;
    if (!v) return obligatorio ? 0 : 1;
    if (*v == '"') {
        v++;
        if (*v == '"') return obligatorio ? 0 : 1;
        *out = (int)strtol(v, &e, 10);
        if (e == v) return 0;
        return 1;
    }
    if (*v == '-' || (*v >= '0' && *v <= '9')) {
        *out = atoi(v);
        return 1;
    }
    return 0;
}

static double leer_porc(const char *obj, const char *end) {
    char buf[64], *q;
    const char *v = json_valor(obj, end, "porc");
    int n = 0;
    if (!v) return 0;
    if (*v == '"') {
        v++;
        while (*v && *v != '"' && n < 63) buf[n++] = *v++;
    } else {
        while (*v && *v != ',' && *v != '}' && n < 63) buf[n++] = *v++;
    }
    buf[n] = 0;
    for (q = buf; *q; q++) if (*q == ',') *q = '.';
    return atof(buf);
}

static int analizar_numeros(const char *texto, int *out, int max) {
    char buf[4096], *p;
    int n = 0, i, j;
    snprintf(buf, sizeof buf, "%s", texto ? texto : "");
    for (p = buf; *p; p++) if (*p == ',') *p = ' ';
    p = buf;
    while (*p && n < max) {
        char *start, *dash;
        while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r') p++;
        if (!*p) break;
        start = p;
        while (*p && *p != ' ' && *p != '\t' && *p != '\n' && *p != '\r') p++;
        if (*p) *p++ = 0;
        dash = strchr(start, '-');
        if (dash && dash != start) {
            char *e1, *e2;
            long a, b;
            *dash = 0;
            a = strtol(start, &e1, 10);
            b = strtol(dash + 1, &e2, 10);
            if (e1 != start && !*e1 && e2 != dash + 1 && !*e2 && a <= b) {
                for (; a <= b && n < max; a++) out[n++] = (int)a;
                continue;
            }
            *dash = '-';
        }
        if (start[0] >= '0' && start[0] <= '9') out[n++] = atoi(start);
    }
    for (i = 1; i < n; i++) {
        int x = out[i];
        j = i;
        while (j > 0 && out[j - 1] > x) { out[j] = out[j - 1]; j--; }
        out[j] = x;
    }
    for (i = 1, j = 0; i < n; i++) if (out[i] != out[j]) out[++j] = out[i];
    return n ? j + 1 : 0;
}

static int cmp_int(const void *A, const void *B) {
    return *(const int *)A - *(const int *)B;
}

static int tipo_de(const char *nombre, int k, int *t, int *m, char *err) {
    static const struct { const char *e; int t, m; } T[] = {
        {"5 si 6", 5, 6}, {"4 si 6", 4, 6}, {"3 si 6", 3, 6},
        {"5 si 5", 5, 5}, {"4 si 5", 4, 5}, {"3 si 5", 3, 5},
        {"4 si 4", 4, 4}, {"3 si 4", 3, 4}, {"3 si 3", 3, 3},
        {"Al 5 (n-1)", 0, 0},
    };
    int i;
    for (i = 0; i < 10; i++) if (strcmp(nombre, T[i].e) == 0) {
        if (T[i].t == 0) {
            if (k < 2) { snprintf(err, 180, "Con Al 5 (n-1), k tiene que ser al menos 2."); return 0; }
            *t = k - 1; *m = k; return 1;
        }
        *t = T[i].t; *m = T[i].m; return 1;
    }
    snprintf(err, 180, "Elige una garantía.");
    return 0;
}

static int parse_grupos(const char *texto, const int *base, int nbase, int v, int k, Grupo *out, int *ng, char *err) {
    char buf[4096], *lin;
    *ng = 0;
    snprintf(buf, sizeof buf, "%s", texto ? texto : "");
    lin = buf;
    while (lin && *lin) {
        char *siguiente = strchr(lin, '\n');
        if (siguiente) *siguiente++ = 0; else siguiente = lin + strlen(lin);
        char *p1, *p2, *p3;
        int nums[MAXN], cn, i, min_a, max_a;
        uint64_t mask = 0;
        while (*lin == '\r' || *lin == ' ') lin++;
        if (*lin) {
            p1 = lin;
            p2 = strchr(lin, ';');
            if (!p2) p2 = strchr(lin, '|');
            if (!p2) { snprintf(err, 180, "Cada grupo va en una línea: numeros ; minimo ; maximo"); return 0; }
            *p2++ = 0;
            p3 = strchr(p2, ';');
            if (!p3) p3 = strchr(p2, '|');
            if (!p3) { snprintf(err, 180, "Cada grupo va en una línea: numeros ; minimo ; maximo"); return 0; }
            *p3++ = 0;
            cn = analizar_numeros(p1, nums, MAXN);
            min_a = atoi(p2);
            max_a = atoi(p3);
            if (!cn) { snprintf(err, 180, "El grupo necesita números entre 1 y %d.", v); return 0; }
            for (i = 0; i < cn; i++) {
                int absn = nums[i];
                if (nbase) {
                    int j, hallado = 0;
                    for (j = 0; j < nbase; j++) if (base[j] == nums[i]) { absn = j + 1; hallado = 1; break; }
                    if (!hallado) { snprintf(err, 180, "El grupo tiene que usar números de la base marcada."); return 0; }
                } else if (absn < 1 || absn > v) {
                    snprintf(err, 180, "El grupo necesita números entre 1 y %d.", v);
                    return 0;
                }
                mask |= 1ull << (absn - 1);
            }
            if (min_a < 0 || min_a > max_a || min_a > k) {
                snprintf(err, 180, "El mínimo tiene que estar entre 0 y %d, y no puede superar al máximo.", k);
                return 0;
            }
            if (*ng >= 32) { snprintf(err, 180, "Demasiados grupos."); return 0; }
            out[*ng].mask = mask;
            out[*ng].min_a = min_a;
            out[*ng].max_a = max_a;
            (*ng)++;
        }
        lin = siguiente;
    }
    return 1;
}

static void filtros_desde(const char *payload, const char *fin, const char *incluir, Filtros *f) {
    const char *fo = NULL, *ff = NULL;
    const char *v = json_valor(payload, fin, "filtros");
    filtros_init(f);
    if (v && *v == '{') objeto_fin(v, &ff), fo = v;
    if (!fo) return;
    if (json_bool(fo, ff, "suma")) {
        leer_int(fo, ff, "suma0", &f->suma_min, 0);
        leer_int(fo, ff, "suma1", &f->suma_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "pares")) {
        leer_int(fo, ff, "pares0", &f->pares_min, 0);
        leer_int(fo, ff, "pares1", &f->pares_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "bajos")) {
        leer_int(fo, ff, "bajos0", &f->bajos_min, 0);
        leer_int(fo, ff, "bajos1", &f->bajos_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "dist")) {
        leer_int(fo, ff, "dist0", &f->dist_min, 0);
        leer_int(fo, ff, "dist1", &f->dist_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "seguidos")) {
        leer_int(fo, ff, "seguidos0", &f->seguidos_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "decenas")) {
        leer_int(fo, ff, "decenas0", &f->decena_max, 0);
        f->activo = 1;
    }
    if (json_bool(fo, ff, "term")) {
        leer_int(fo, ff, "term0", &f->term_max, 0);
        f->activo = 1;
    }
    f->nincluir = analizar_numeros(incluir, f->incluir, MAXN);
    if (f->nincluir) f->activo = 1;
}

static int parse_datos(const char *json, Job *job, char *err) {
    const char *pay, *fin = NULL;
    char tipo[64], grupos[4096], incluir[512], modo[8];
    int i, j, base_num = 0;
    memset(job, 0, sizeof *job);
    filtros_init(&job->filtros);
    pay = json_valor(json, NULL, "payload");
    if (!pay || *pay != '{' || !objeto_fin(pay, &fin)) pay = json, fin = NULL;
    if (!json_str(pay, fin, "tipo", tipo, sizeof tipo)) tipo[0] = 0;
    if (!leer_int(pay, fin, "k", &job->k, 1)) { snprintf(err, 180, "k tiene que estar entre 1 y el tamaño de la base."); return 0; }
    if (!tipo_de(tipo, job->k, &job->t, &job->m, err)) return 0;
    job->nbase = json_ints(pay, fin, "marcados", job->base, MAXN);
    qsort(job->base, (size_t)job->nbase, sizeof(int), cmp_int);
    for (i = 1, j = 0; i < job->nbase; i++) if (job->base[i] != job->base[j]) job->base[++j] = job->base[i];
    if (job->nbase) job->nbase = j + 1;
    if (!job->nbase) {
        if (!leer_int(pay, fin, "base", &base_num, 1)) base_num = 0;
        job->v = base_num;
    } else job->v = job->nbase;
    if (job->v < 1 || job->v > MAXN) { snprintf(err, 180, "La base en lenguaje máquina llega hasta %d.", MAXN); return 0; }
    if (job->k < 1 || job->k > job->v) { snprintf(err, 180, "k tiene que estar entre 1 y el tamaño de la base."); return 0; }
    if (job->m < 1 || job->m > job->v || job->t < 1 || job->t > job->k || job->t > job->m) {
        snprintf(err, 180, "La garantía %d si %d no cabe en v=%d y k=%d.", job->t, job->m, job->v, job->k);
        return 0;
    }
    json_str(pay, fin, "grupos", grupos, sizeof grupos);
    json_str(pay, fin, "incluir", incluir, sizeof incluir);
    if (!parse_grupos(grupos, job->base, job->nbase, job->v, job->k, job->grupos, &job->ngrupos, err)) return 0;
    filtros_desde(pay, fin, incluir, &job->filtros);
    if (!leer_int(pay, fin, "cantidad", &job->cantidad, 0)) { snprintf(err, 180, "Dato numérico no válido."); return 0; }
    job->porc = leer_porc(pay, fin);
    job->ciclos = json_bool(pay, fin, "ciclos");
    job->usar_record = json_bool(pay, fin, "usar_record");
    if (!json_str(pay, fin, "modo", modo, sizeof modo)) strcpy(modo, "n");
    job->modo_p = modo[0] == 'p';
    return 1;
}

static int pasa_filtros(int *nums, int nr, const Filtros *f, int v) {
    int i, total = 0, pares = 0, seguidos = 0, bajos = 0, mitad;
    if (!f || !f->activo) return 1;
    for (i = 1; i < nr; i++) {
        int x = nums[i], j = i;
        while (j > 0 && nums[j - 1] > x) { nums[j] = nums[j - 1]; j--; }
        nums[j] = x;
    }
    for (i = 0; i < nr; i++) total += nums[i];
    if (f->suma_min != INT_MIN && total < f->suma_min) return 0;
    if (f->suma_max != INT_MIN && total > f->suma_max) return 0;
    for (i = 0; i < nr; i++) if (nums[i] % 2 == 0) pares++;
    if (f->pares_min != INT_MIN && pares < f->pares_min) return 0;
    if (f->pares_max != INT_MIN && pares > f->pares_max) return 0;
    for (i = 1; i < nr; i++) if (nums[i] == nums[i - 1] + 1) seguidos++;
    if (f->seguidos_max != INT_MIN && seguidos > f->seguidos_max) return 0;
    mitad = v / 2; if (mitad < 1) mitad = 1;
    for (i = 0; i < nr; i++) if (nums[i] <= mitad) bajos++;
    if (f->bajos_min != INT_MIN && bajos < f->bajos_min) return 0;
    if (f->bajos_max != INT_MIN && bajos > f->bajos_max) return 0;
    if (f->decena_max != INT_MIN) {
        int dec[8] = {0};
        for (i = 0; i < nr; i++) {
            int d = (nums[i] - 1) / 10;
            if (d < 0) d = 0;
            if (d > 7) d = 7;
            if (++dec[d] > f->decena_max) return 0;
        }
    }
    if (f->term_max != INT_MIN) {
        int fin[10] = {0};
        for (i = 0; i < nr; i++) if (++fin[nums[i] % 10] > f->term_max) return 0;
    }
    if (nr >= 2 && (f->dist_min != INT_MIN || f->dist_max != INT_MIN)) {
        int mn = 999, mx = 0;
        for (i = 1; i < nr; i++) {
            int d = nums[i] - nums[i - 1];
            if (d < mn) mn = d;
            if (d > mx) mx = d;
        }
        if (f->dist_min != INT_MIN && mn < f->dist_min) return 0;
        if (f->dist_max != INT_MIN && mx > f->dist_max) return 0;
    }
    for (i = 0; i < f->nincluir; i++) {
        int j, ok = 0;
        for (j = 0; j < nr; j++) if (nums[j] == f->incluir[i]) ok = 1;
        if (!ok) return 0;
    }
    return 1;
}

static int lista_add(Lista *L, int v) {
    if (L->n >= L->cap) {
        int nc = L->cap ? L->cap * 2 : 256;
        int *p = (int *)realloc(L->idx, (size_t)nc * sizeof(int));
        if (!p) return 0;
        L->idx = p;
        L->cap = nc;
    }
    L->idx[L->n++] = v;
    return 1;
}

static uint64_t muestra(int v, int k) {
    int a[MAXN], i;
    uint64_t bits = 0;
    for (i = 0; i < v; i++) a[i] = i + 1;
    for (i = 0; i < k; i++) {
        int j = i + (int)(rnd64() % (uint64_t)(v - i));
        int tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
        bits |= 1ull << (a[i] - 1);
    }
    return bits;
}

static int listar(uint64_t bits, int v, int *out) {
    int n = 0, i;
    for (i = 0; i < v && i < MAXN; i++) if (bits & (1ull << i)) out[n++] = i + 1;
    return n;
}

static int valida(Opt *o, uint64_t bits) {
    int crudos[MAXN], reales[MAXN], nr, i;
    if (!o->filtros.activo && !o->ngrupos) return 1;
    nr = listar(bits, o->v, crudos);
    for (i = 0; i < nr; i++) reales[i] = o->tiene_mapa ? o->mapa[crudos[i] - 1] : crudos[i];
    if (!pasa_filtros(reales, nr, &o->filtros, o->filtro_v)) return 0;
    for (i = 0; i < o->ngrupos; i++) {
        int ac = __builtin_popcountll(bits & o->grupos[i].mask);
        if (ac < o->grupos[i].min_a || ac > o->grupos[i].max_a) return 0;
    }
    return 1;
}

static void aplicar(Opt *o, uint64_t bits, int signo) {
    int n;
    if (++o->sello == 0) {
        memset(o->visto, 0, (size_t)o->universo_n * sizeof(unsigned));
        o->sello = 1;
    }
    for (n = 1; n <= o->v; n++) {
        Lista *L;
        int j;
        if ((bits & (1ull << (n - 1))) == 0) continue;
        L = &o->por[n];
        for (j = 0; j < L->n; j++) {
            int i = L->idx[j];
            int antes, ahora;
            if (o->visto[i] == o->sello) continue;
            o->visto[i] = o->sello;
            if (__builtin_popcountll(bits & o->universo[i]) < o->t) continue;
            antes = o->conteos[i];
            ahora = antes + signo;
            o->conteos[i] = ahora;
            if (antes == 0 && ahora == 1) o->cubiertos++;
            else if (antes == 1 && ahora == 0) o->cubiertos--;
        }
    }
}

static int ganancia(Opt *o, int idx, uint64_t nueva) {
    uint64_t antigua = o->ap[idx];
    uint64_t cambiados = antigua ^ nueva;
    int n, g = 0;
    if (!cambiados) return 0;
    if (++o->sello == 0) {
        memset(o->visto, 0, (size_t)o->universo_n * sizeof(unsigned));
        o->sello = 1;
    }
    for (n = 1; n <= o->v; n++) {
        Lista *L;
        int j;
        if ((cambiados & (1ull << (n - 1))) == 0) continue;
        L = &o->por[n];
        for (j = 0; j < L->n; j++) {
            int i = L->idx[j];
            int antes, ahora;
            uint64_t sorteo;
            if (o->visto[i] == o->sello) continue;
            o->visto[i] = o->sello;
            sorteo = o->universo[i];
            antes = __builtin_popcountll(antigua & sorteo) >= o->t;
            ahora = __builtin_popcountll(nueva & sorteo) >= o->t;
            if (antes && !ahora) { if (o->conteos[i] == 1) g--; }
            else if (!antes && ahora) { if (o->conteos[i] == 0) g++; }
        }
    }
    return g;
}

static uint64_t mutar(Opt *o, uint64_t bits) {
    int dentro[MAXN], fuera[MAXN], nd = 0, nf = 0, n, q, p;
    for (n = 1; n <= o->v; n++) {
        if (bits & (1ull << (n - 1))) dentro[nd++] = n;
        else fuera[nf++] = n;
    }
    if (!nd || !nf) return bits;
    q = dentro[(int)(rnd64() % (uint64_t)nd)];
    p = fuera[(int)(rnd64() % (uint64_t)nf)];
    bits &= ~(1ull << (q - 1));
    bits |= 1ull << (p - 1);
    return bits;
}

static int crecer(Opt *o) {
    int nc;
    uint64_t *a, *m;
    if (o->nap < o->cap) return 1;
    nc = o->cap ? o->cap * 2 : 64;
    a = (uint64_t *)realloc(o->ap, (size_t)nc * sizeof(uint64_t));
    if (!a) return 0;
    o->ap = a;
    m = (uint64_t *)realloc(o->mejor, (size_t)nc * sizeof(uint64_t));
    if (!m) return 0;
    o->mejor = m;
    o->cap = nc;
    return 1;
}

static int repetida(const Opt *o, uint64_t bits, int salvo) {
    int i;
    for (i = 0; i < o->nap; i++) if (i != salvo && o->ap[i] == bits) return 1;
    return 0;
}

static int agregar(Opt *o, uint64_t bits) {
    if (repetida(o, bits, -1)) return -1;
    if (!crecer(o)) return 0;
    o->ap[o->nap++] = bits;
    aplicar(o, bits, 1);
    return 1;
}

static double cob_de(const Opt *o) {
    if (!o->universo_n) return 0;
    return 100.0 * (double)o->cubiertos / (double)o->universo_n;
}

static void paso(Opt *o) {
    int idx;
    uint64_t antigua, nueva;
    o->ciclos++;
    if (!o->nap) return;
    idx = (int)(rnd64() % (uint64_t)o->nap);
    antigua = o->ap[idx];
    nueva = mutar(o, antigua);
    if (nueva != antigua && valida(o, nueva) && !repetida(o, nueva, idx)) {
        int g = ganancia(o, idx, nueva);
        int acepta = g > 0;
        if (!acepta && o->temp > 0.0001) {
            double u = (double)(rnd64() >> 11) * (1.0 / 9007199254740992.0);
            if (u < exp((double)g / o->temp)) acepta = 1;
        }
        if (acepta) {
            double cob;
            aplicar(o, antigua, -1);
            aplicar(o, nueva, 1);
            o->ap[idx] = nueva;
            cob = cob_de(o);
            if (cob > o->mejor_cob) {
                o->mejor_cob = cob;
                memcpy(o->mejor, o->ap, (size_t)o->nap * sizeof(uint64_t));
                o->mejor_n = o->nap;
            }
        }
    }
    o->temp *= 0.9995;
}

static void opt_free(Opt *o) {
    int n;
    if (!o) return;
    for (n = 0; n <= MAXN; n++) free(o->por[n].idx);
    free(o->universo);
    free(o->conteos);
    free(o->visto);
    free(o->ap);
    free(o->mejor);
    free(o);
}

static uint64_t gcd_u(uint64_t a, uint64_t b) {
    while (b) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static uint64_t combinaciones(int n, int k) {
    uint64_t r = 1;
    int i;
    if (k < 0 || n < 0 || k > n) return 0;
    if (k > n - k) k = n - k;
    for (i = 1; i <= k; i++) {
        uint64_t num = (uint64_t)(n - k + i);
        uint64_t den = (uint64_t)i;
        uint64_t g = gcd_u(num, den);
        num /= g;
        den /= g;
        g = gcd_u(r, den);
        r /= g;
        den /= g;
        if (num && r > UINT64_MAX / num) return UINT64_MAX;
        r *= num;
        if (den > 1) r /= den;
    }
    return r;
}

static int llenar_sorteos(Opt *o) {
    int c[MAXN], i, j, n = 0, m = o->m, v = o->v;
    for (i = 0; i < m; i++) c[i] = i;
    for (;;) {
        uint64_t bits = 0;
        if (n >= o->universo_n) return 0;
        for (i = 0; i < m; i++) bits |= 1ull << c[i];
        o->universo[n] = bits;
        for (j = 0; j < m; j++) if (!lista_add(&o->por[c[j] + 1], n)) return 0;
        n++;
        for (i = m - 1; i >= 0 && c[i] == v - m + i; i--) ;
        if (i < 0) break;
        c[i]++;
        for (j = i + 1; j < m; j++) c[j] = c[j - 1] + 1;
    }
    return n == o->universo_n;
}

static int reservar_universo(Opt *o, int U) {
    int n;
    o->universo_n = U;
    o->universo = (uint64_t *)malloc((size_t)U * sizeof(uint64_t));
    o->conteos = (int *)calloc((size_t)U, sizeof(int));
    o->visto = (unsigned *)calloc((size_t)U, sizeof(unsigned));
    if (!o->universo || !o->conteos || !o->visto) return 0;
    if (o->exacto && o->m >= 1) {
        uint64_t cada = combinaciones(o->v - 1, o->m - 1);
        if (cada > (uint64_t)INT_MAX) return 0;
        for (n = 1; n <= o->v; n++) {
            int *p = (int *)malloc((size_t)cada * sizeof(int));
            if (!p) return 0;
            o->por[n].idx = p;
            o->por[n].cap = (int)cada;
        }
    }
    return 1;
}

static Opt *opt_nuevo(const Job *job) {
    Opt *o = (Opt *)calloc(1, sizeof *o);
    int U, i;
    if (!o) return NULL;
    o->v = job->v; o->k = job->k; o->t = job->t; o->m = job->m;
    o->filtro_v = job->nbase ? 49 : job->v;
    o->tiene_mapa = job->nbase > 0;
    if (o->tiene_mapa) memcpy(o->mapa, job->base, (size_t)job->nbase * sizeof(int));
    o->filtros = job->filtros;
    o->ngrupos = job->ngrupos;
    memcpy(o->grupos, job->grupos, sizeof o->grupos);
    o->temp = 1;
    o->cob_vista = -1;
    o->total_sorteos = combinaciones(o->v, o->m);
    o->exacto = o->total_sorteos > 0 && o->total_sorteos <= (uint64_t)MAX_SORTEOS
        && o->total_sorteos <= (uint64_t)INT_MAX && o->m >= 1;
    U = o->exacto ? (int)o->total_sorteos : UNIVERSO_DEF;
    if (!reservar_universo(o, U)) {
        if (!o->exacto) { opt_free(o); return NULL; }
        opt_free(o);
        o = (Opt *)calloc(1, sizeof *o);
        if (!o) return NULL;
        o->v = job->v; o->k = job->k; o->t = job->t; o->m = job->m;
        o->filtro_v = job->nbase ? 49 : job->v;
        o->tiene_mapa = job->nbase > 0;
        if (o->tiene_mapa) memcpy(o->mapa, job->base, (size_t)job->nbase * sizeof(int));
        o->filtros = job->filtros;
        o->ngrupos = job->ngrupos;
        memcpy(o->grupos, job->grupos, sizeof o->grupos);
        o->temp = 1;
        o->cob_vista = -1;
        o->total_sorteos = combinaciones(o->v, o->m);
        o->exacto = 0;
        if (!reservar_universo(o, UNIVERSO_DEF)) { opt_free(o); return NULL; }
    }
    if (o->exacto) {
        if (!llenar_sorteos(o)) { opt_free(o); return NULL; }
    } else {
        for (i = 0; i < o->universo_n; i++) {
            uint64_t s = muestra(o->v, o->m);
            int n;
            o->universo[i] = s;
            for (n = 1; n <= o->v; n++) if (s & (1ull << (n - 1))) lista_add(&o->por[n], i);
        }
    }
    return o;
}

static void fijar_nota(uint64_t total, int exacto) {
    EnterCriticalSection(&g_cs);
    g_exacto = exacto;
    if (!total) g_nota[0] = 0;
    else if (exacto) snprintf(g_nota, sizeof g_nota, "sobre %llu sorteos", (unsigned long long)total);
    else snprintf(g_nota, sizeof g_nota, "estimación, %llu sorteos", (unsigned long long)total);
    LeaveCriticalSection(&g_cs);
}

static double cubrir_lista(const uint64_t *bets, int nb, int v, int m, int t, uint64_t total) {
    int c[MAXN], i, j;
    uint64_t hit = 0, visto = 0;
    if (!total || total > 80000000ull || m < 1 || m > v) return -1;
    for (i = 0; i < m; i++) c[i] = i;
    for (;;) {
        uint64_t bits = 0;
        int cubre = 0;
        for (i = 0; i < m; i++) bits |= 1ull << c[i];
        for (j = 0; j < nb; j++) if (__builtin_popcountll(bets[j] & bits) >= t) { cubre = 1; break; }
        hit += (uint64_t)cubre;
        visto++;
        for (i = m - 1; i >= 0 && c[i] == v - m + i; i--) ;
        if (i < 0) break;
        c[i]++;
        for (j = i + 1; j < m; j++) c[j] = c[j - 1] + 1;
    }
    if (visto != total) return -1;
    return 100.0 * (double)hit / (double)total;
}

static void volcar(Opt *o, const Job *job, double cob);

static void generar(Opt *o, const Job *job, int cantidad) {
    int gen = 0, intentos = 0, maxi = cantidad * 2000;
    char buf[180];
    snprintf(buf, sizeof buf, "Generando %d apuestas.", cantidad);
    anotar(buf);
    while (gen < cantidad && intentos < maxi && !g_parar) {
        uint64_t bits = muestra(o->v, o->k);
        intentos++;
        if (!valida(o, bits)) continue;
        {
            int metio = agregar(o, bits);
            if (metio == 0) break;
            if (metio < 0) continue;
        }
        gen++;
        if (gen == cantidad || (gen % 20) == 0) {
            double cob = cob_de(o);
            snprintf(buf, sizeof buf, "Progreso: %d/%d | Cobertura actual: %.4f%%", gen, cantidad, cob);
            progreso(buf, o->exacto ? cob : -1);
            volcar(o, job, o->exacto ? cob : -1);
        }
    }
    if (g_parar) {
        snprintf(buf, sizeof buf, "Generación detenida. Apuestas conseguidas: %d.", gen);
        anotar(buf);
    }
}

static int reponer(Opt *o, int meta) {
    int i, intentos = 0, maxi = meta * 4000;
    for (i = o->nap - 1; i >= 0; i--) aplicar(o, o->ap[i], -1);
    o->nap = 0;
    o->temp = 1;
    while (o->nap < meta && intentos < maxi && !g_parar) {
        uint64_t bits = muestra(o->v, o->k);
        int metio;
        intentos++;
        if (!valida(o, bits)) continue;
        metio = agregar(o, bits);
        if (metio == 0) return 0;
    }
    return o->nap == meta;
}

static void guardar_mejor(Opt *o) {
    double cob = cob_de(o);
    if (cob > o->mejor_cob && o->cap >= o->nap) {
        o->mejor_cob = cob;
        memcpy(o->mejor, o->ap, (size_t)o->nap * sizeof(uint64_t));
        o->mejor_n = o->nap;
    }
}

/* Cambia dos números. Se queda con el primer cambio que cubre más sorteos. */
static int escalar(Opt *o) {
    int b, i, j, x, y, nd, nf;
    int dentro[MAXN], fuera[MAXN];
    if (o->k < 2 || o->v - o->k < 2) return 0;
    for (b = 0; b < o->nap && !g_parar; b++) {
        int n, t;
        nd = listar(o->ap[b], o->v, dentro);
        nf = 0;
        for (n = 1; n <= o->v; n++) {
            int esta = 0;
            for (t = 0; t < nd; t++) if (dentro[t] == n) esta = 1;
            if (!esta) fuera[nf++] = n;
        }
        for (i = 0; i < nd; i++) for (j = i + 1; j < nd; j++)
        for (x = 0; x < nf; x++) for (y = x + 1; y < nf; y++) {
            uint64_t nueva = o->ap[b];
            nueva &= ~(1ull << (dentro[i] - 1));
            nueva &= ~(1ull << (dentro[j] - 1));
            nueva |= 1ull << (fuera[x] - 1);
            nueva |= 1ull << (fuera[y] - 1);
            if (!valida(o, nueva) || repetida(o, nueva, b)) continue;
            if (ganancia(o, b, nueva) > 0) {
                aplicar(o, o->ap[b], -1);
                aplicar(o, nueva, 1);
                o->ap[b] = nueva;
                guardar_mejor(o);
                return 1;
            }
        }
    }
    return 0;
}

/* Un sorteo sin cubrir presta sus t primeros números a un boleto al azar. */
static int golpe(Opt *o) {
    int i, b, nn, toma, n, intentos;
    int nums[MAXN];
    uint64_t nuevo, sorteo;
    for (i = 0; i < o->universo_n; i++) if (!o->conteos[i]) break;
    if (i >= o->universo_n || o->k < 1 || o->nap < 1) return 0;
    sorteo = o->universo[i];
    nn = listar(sorteo, o->v, nums);
    if (nn <= 0) return 0;
    toma = o->t < o->k ? o->t : o->k;
    if (toma > nn) toma = nn;
    for (intentos = 0; intentos < 20; intentos++) {
        nuevo = 0;
        for (n = 0; n < toma; n++) nuevo |= 1ull << (nums[n] - 1);
        n = 0;
        while (__builtin_popcountll(nuevo) < o->k && n < 10000) {
            nuevo |= 1ull << (int)(rnd64() % (uint64_t)o->v);
            n++;
        }
        if (__builtin_popcountll(nuevo) != o->k || !valida(o, nuevo)) continue;
        b = (int)(rnd64() % (uint64_t)o->nap);
        if (o->ap[b] == nuevo || repetida(o, nuevo, b)) continue;
        aplicar(o, o->ap[b], -1);
        aplicar(o, nuevo, 1);
        o->ap[b] = nuevo;
        guardar_mejor(o);
        return 1;
    }
    return 0;
}

static void restaurar(Opt *o) {
    int i;
    if (o->mejor_n <= 0) return;
    for (i = o->nap - 1; i >= 0; i--) aplicar(o, o->ap[i], -1);
    o->nap = 0;
    o->temp = 1;
    for (i = 0; i < o->mejor_n; i++) if (!agregar(o, o->mejor[i])) break;
}

/* En bases pequeñas la escalada llega al 100% con las apuestas pedidas.
   Pegar dos reducidas de mitades no vale: un sorteo 3+3 no cae en ninguna. */
static int cubrir_objetivo(const Opt *o, double objetivo) {
    double cob = cob_de(o);
    return cob >= 99.9995 || (objetivo >= 0 && cob >= objetivo);
}

static int buscar_local(Opt *o, double objetivo) {
    int ronda, tope, prueba, meta;
    char buf[180];
    if (!o->exacto || o->universo_n > 20000 || o->nap > 48 || o->k < 2) return 0;
    if (cubrir_objetivo(o, objetivo)) return 1;
    meta = o->nap;
    tope = o->universo_n <= 2000 ? 70 : 8;
    anotar("Optimizando. Cambio dos números de una apuesta.");
    for (prueba = 0; prueba < 4 && !g_parar; prueba++) {
        if (prueba) {
            snprintf(buf, sizeof buf, "Intento %d. El anterior se quedó en %.4f%%.", prueba + 1, o->mejor_cob);
            anotar(buf);
            if (!reponer(o, meta)) break;
        }
        for (ronda = 0; ronda < tope && !g_parar; ronda++) {
            while (escalar(o) && !g_parar) {
                if (cubrir_objetivo(o, objetivo)) return 1;
            }
            snprintf(buf, sizeof buf, "Ronda %d | Cobertura: %.4f%%", ronda + 1, cob_de(o));
            progreso(buf, cob_de(o));
            if (cubrir_objetivo(o, objetivo)) return 1;
            if (!golpe(o)) break;
            if (cubrir_objetivo(o, objetivo)) return 1;
        }
    }
    restaurar(o);
    return cubrir_objetivo(o, objetivo);
}

static void optimizar(Opt *o, const Job *job, double objetivo) {
    char buf[200];
    if (!o->nap) return;
    o->mejor_cob = cob_de(o);
    if (o->cap < o->nap) return;
    memcpy(o->mejor, o->ap, (size_t)o->nap * sizeof(uint64_t));
    o->mejor_n = o->nap;
    if (buscar_local(o, objetivo)) {
        double marca = o->mejor_cob;
        if (marca >= 99.9995) snprintf(buf, sizeof buf, "Cobertura %.4f%%. Cubre todos los sorteos.", marca);
        else snprintf(buf, sizeof buf, "Cobertura %.4f%% alcanza el objetivo %.4f%%.", marca, objetivo);
        anotar(buf);
        progreso(buf, marca);
        volcar(o, job, marca);
        return;
    }
    anotar("Optimizando. Pulsa Parar para guardar el mejor récord.");
    {
        unsigned long long ultima = 0;
        int quieto = 0, intento = 1, meta = o->nap, patadas = 0;
        while (!g_parar) {
            double antes = o->mejor_cob;
            double marca;
            paso(o);
            if (o->temp <= 0.0001 && o->mejor_cob <= antes) quieto++;
            else {
                if (o->mejor_cob > antes) patadas = 0;
                quieto = 0;
            }
            if (!o->exacto && (GetTickCount64() - ultima) >= 2000) {
                double real = cubrir_lista(o->mejor_n ? o->mejor : o->ap, o->mejor_n ? o->mejor_n : o->nap, o->v, o->m, o->t, o->total_sorteos);
                ultima = GetTickCount64();
                if (real >= 0) o->cob_vista = real;
            }
            marca = o->exacto ? o->mejor_cob : o->cob_vista;
            if (g_tope && o->ciclos >= g_tope) break;
            if (marca >= 99.9995 || (objetivo >= 0 && marca >= objetivo)) {
                if (marca >= 99.9995) snprintf(buf, sizeof buf, "Cobertura %.4f%%. Cubre todos los sorteos.", marca);
                else snprintf(buf, sizeof buf, "Cobertura %.4f%% alcanza el objetivo %.4f%%.", marca, objetivo);
                anotar(buf);
                progreso(buf, marca);
                volcar(o, job, marca);
                break;
            }
            if ((o->ciclos % 100ull) == 0) {
                int real = o->exacto || o->cob_vista >= 0;
                double cob = o->exacto ? o->mejor_cob : o->cob_vista;
                if (real) snprintf(buf, sizeof buf, "Ciclo: %llu | Récord Cobertura: %.4f%% | Temp: %.4f", o->ciclos, cob, o->temp);
                else snprintf(buf, sizeof buf, "Ciclo: %llu | Contando los %llu sorteos | Temp: %.4f", o->ciclos, (unsigned long long)o->total_sorteos, o->temp);
                progreso(buf, real ? cob : -1);
                volcar(o, job, real ? cob : -1);
            }
            if (quieto >= 1500 && o->temp <= 0.0001 && marca < 99.9995 && (objetivo < 0 || marca < objetivo)) {
                if (patadas < 8 && golpe(o)) {
                    patadas++;
                    o->temp = 1;
                    quieto = 0;
                    anotar("Reescribo una apuesta hacia un sorteo que aún no está cubierto.");
                } else {
                    intento++;
                    patadas = 0;
                    snprintf(buf, sizeof buf, "Intento %d. El anterior se quedó en %.4f%%.", intento, o->mejor_cob);
                    anotar(buf);
                    if (!reponer(o, meta)) break;
                    quieto = 0;
                }
            }
        }
    }
    if (g_parar) anotar("Optimización detenida. Guardando el mejor récord.");
}

static uint64_t mapear(const Job *job, uint64_t bits) {
    uint64_t real = 0;
    int j;
    if (!job->nbase) return bits;
    for (j = 0; j < job->v && j < MAXN; j++) if (bits & (1ull << j)) {
        int num = job->base[j];
        if (num >= 1 && num <= MAXN) real |= 1ull << (num - 1);
    }
    return real;
}

static int cmp_fila(const void *A, const void *B) {
    const Fila *a = (const Fila *)A, *b = (const Fila *)B;
    int m = a->k < b->k ? a->k : b->k, i;
    for (i = 0; i < m; i++) if (a->n[i] != b->n[i]) return a->n[i] - b->n[i];
    return a->k - b->k;
}

static int escribir(uint64_t *bets, int n, int v, int k, int t, double cob, const char *marca, char *nombre) {
    Fila *filas;
    FILE *f;
    SYSTEMTIME st;
    int i, j;
    (void)v;
    filas = (Fila *)malloc((size_t)n * sizeof(Fila));
    if (!filas) return 0;
    for (i = 0; i < n; i++) {
        filas[i].k = 0;
        for (j = 0; j < MAXN; j++) if (bets[i] & (1ull << j)) filas[i].n[filas[i].k++] = j + 1;
    }
    qsort(filas, (size_t)n, sizeof(Fila), cmp_fila);
    GetLocalTime(&st);
    if (marca && marca[0])
        snprintf(nombre, 240, "LOTTO_v%d_k%d_t%d_%s_%04d%02d%02d_%02d%02d%02d.txt",
            v, k, t, marca, st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
    else
        snprintf(nombre, 240, "LOTTO_v%d_k%d_t%d_%.4fpct_%04d%02d%02d_%02d%02d%02d.txt",
            v, k, t, cob, st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
    f = fopen(nombre, "wb");
    if (!f) { free(filas); return 0; }
    for (i = 0; i < n; i++) {
        for (j = 0; j < filas[i].k; j++) fprintf(f, "%s%02d", j ? " " : "", filas[i].n[j]);
        fputc('\n', f);
    }
    fclose(f);
    free(filas);
    return 1;
}

static void publicar_bets(uint64_t *b, int n, int k, double cob) {
    EnterCriticalSection(&g_cs);
    free(g_bets);
    g_bets = b;
    g_nbets = n;
    g_apuestas = n;
    g_k = k;
    if (cob >= 0) snprintf(g_cob, sizeof g_cob, "%.4f%%", cob);
    LeaveCriticalSection(&g_cs);
}

static void volcar(Opt *o, const Job *job, double cob) {
    uint64_t *src, *reales;
    int n, i;
    if (o->mejor_n > 0) { src = o->mejor; n = o->mejor_n; }
    else { src = o->ap; n = o->nap; }
    if (!n) return;
    reales = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));
    if (!reales) return;
    for (i = 0; i < n; i++) reales[i] = mapear(job, src[i]);
    publicar_bets(reales, n, job->k, cob);
    fijar_nota(o->total_sorteos, o->exacto || o->cob_vista >= 0);
}

static void guardar_opt(Opt *o, Job *job, const char *marca) {
    uint64_t *src, *reales;
    int n, i;
    double cob;
    int medido;
    char nombre[260], msg[320];
    if (o->mejor_n > 0) { src = o->mejor; n = o->mejor_n; cob = o->mejor_cob; }
    else { src = o->ap; n = o->nap; cob = cob_de(o); }
    medido = o->exacto;
    if (!o->exacto) {
        double real = cubrir_lista(src, n, o->v, o->m, o->t, o->total_sorteos);
        if (real >= 0) { cob = real; medido = 1; }
    }
    if (!n) { anotar("No hay apuestas que guardar."); return; }
    reales = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));
    if (!reales) { anotar("Error: sin memoria."); return; }
    for (i = 0; i < n; i++) reales[i] = mapear(job, src[i]);
    if (!escribir(reales, n, job->v, job->k, job->t, cob, marca, nombre)) {
        free(reales);
        anotar("Error: no se ha podido guardar.");
        return;
    }
    publicar_bets(reales, n, job->k, cob);
    fijar_nota(o->total_sorteos, medido);
    g_v = job->v; g_t = job->t;
    snprintf(msg, sizeof msg, "Archivo: %s", nombre);
    anotar(msg);
}

static int apuestas_de_url(const char *url) {
    const char *p;
    int n = 0;
    if (!url) return 0;
    p = strstr(url, "por-");
    if (!p) return 0;
    for (p += 4; (*p >= '0' && *p <= '9') || *p == '.'; p++) if (*p != '.') {
        if (n > 100000000) return 0;
        n = n * 10 + (*p - '0');
    }
    return n;
}

static const char *buscar_url(int v, int k, int t, int m) {
    int i;
    for (i = 0; i < NRED; i++)
        if (REDUCIDAS[i].v == v && REDUCIDAS[i].k == k && REDUCIDAS[i].t == t && REDUCIDAS[i].m == m)
            return REDUCIDAS[i].url;
    return NULL;
}

static void unir_ruta(wchar_t *dst, int cap, const wchar_t *path, const wchar_t *extra) {
    int i = 0;
    const wchar_t *ps;
    for (ps = path; *ps && i < cap - 1; ps++) dst[i++] = *ps;
    for (ps = extra; *ps && i < cap - 1; ps++) dst[i++] = *ps;
    dst[i] = 0;
}

static int http_bajar(const char *url, unsigned char **out, int *nlen, char *err) {
    char actual[2048];
    unsigned char *buf = NULL;
    int salto, n = 0, cap = 0, ok = 0;
    *out = NULL; *nlen = 0;
    snprintf(actual, sizeof actual, "%s", url);
    for (salto = 0; salto < 5; salto++) {
        wchar_t wurl[2048], host[300], path[1800], extra[800], full[2200], wloc[2048];
        URL_COMPONENTS uc;
        HINTERNET ses = NULL, con = NULL, req = NULL;
        DWORD flags, status = 0, sz, pol;
        char loc[2048];
        int seguir = 0;
        buf = NULL; n = 0; cap = 0;
        if (!MultiByteToWideChar(CP_UTF8, 0, actual, -1, wurl, 2048)) { snprintf(err, 180, "url"); return 0; }
        memset(&uc, 0, sizeof uc);
        uc.dwStructSize = sizeof uc;
        uc.lpszHostName = host; uc.dwHostNameLength = 299;
        uc.lpszUrlPath = path; uc.dwUrlPathLength = 1799;
        uc.lpszExtraInfo = extra; uc.dwExtraInfoLength = 799;
        if (!WinHttpCrackUrl(wurl, 0, 0, &uc)) { snprintf(err, 180, "No se ha podido descargar la reducida."); return 0; }
        if (uc.dwHostNameLength < 300) host[uc.dwHostNameLength] = 0;
        if (uc.dwUrlPathLength < 1800) path[uc.dwUrlPathLength] = 0;
        if (uc.dwExtraInfoLength < 800) extra[uc.dwExtraInfoLength] = 0;
        ses = WinHttpOpen(L"Mozilla/5.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
        if (!ses) { snprintf(err, 180, "No se ha podido descargar la reducida."); return 0; }
        WinHttpSetTimeouts(ses, 10000, 10000, 30000, 120000);
        {
            DWORD prot = WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_2;
            WinHttpSetOption(ses, WINHTTP_OPTION_SECURE_PROTOCOLS, &prot, sizeof prot);
        }
        con = WinHttpConnect(ses, host, uc.nPort, 0);
        if (!con) { WinHttpCloseHandle(ses); snprintf(err, 180, "No se ha podido descargar la reducida."); return 0; }
        unir_ruta(full, 2200, path, extra);
        flags = (uc.nScheme == INTERNET_SCHEME_HTTPS) ? WINHTTP_FLAG_SECURE : 0;
        req = WinHttpOpenRequest(con, L"GET", full, NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, flags);
        pol = WINHTTP_OPTION_REDIRECT_POLICY_NEVER;
        if (req) WinHttpSetOption(req, WINHTTP_OPTION_REDIRECT_POLICY, &pol, sizeof pol);
        if (!req || !WinHttpSendRequest(req, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0) || !WinHttpReceiveResponse(req, NULL)) {
            if (req) WinHttpCloseHandle(req);
            WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
            snprintf(err, 180, "No se ha podido descargar la reducida.");
            return 0;
        }
        sz = sizeof status;
        WinHttpQueryHeaders(req, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER, WINHTTP_HEADER_NAME_BY_INDEX, &status, &sz, WINHTTP_NO_HEADER_INDEX);
        if (status >= 300 && status < 400) {
            sz = sizeof wloc;
            if (WinHttpQueryHeaders(req, WINHTTP_QUERY_LOCATION, WINHTTP_HEADER_NAME_BY_INDEX, wloc, &sz, WINHTTP_NO_HEADER_INDEX)) {
                WideCharToMultiByte(CP_UTF8, 0, wloc, -1, loc, sizeof loc, NULL, NULL);
                if (strncmp(loc, "http", 4) == 0) { snprintf(actual, sizeof actual, "%s", loc); seguir = 1; }
            }
        }
        if (seguir) {
            WinHttpCloseHandle(req); WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
            continue;
        }
        if (status != 200) {
            snprintf(err, 180, "No se ha podido descargar la reducida (%lu).", status);
            WinHttpCloseHandle(req); WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
            return 0;
        }
        for (;;) {
            DWORD avail = 0, got = 0;
            if (!WinHttpQueryDataAvailable(req, &avail) || !avail) break;
            if (n + (int)avail > cap) {
                int nc = cap ? cap * 2 : 65536;
                unsigned char *nb;
                while (nc < n + (int)avail) nc *= 2;
                if (nc > 32 * 1024 * 1024) {
                    snprintf(err, 180, "el zip es demasiado grande");
                    WinHttpCloseHandle(req); WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
                    free(buf);
                    return 0;
                }
                nb = (unsigned char *)realloc(buf, (size_t)nc);
                if (!nb) {
                    snprintf(err, 180, "sin memoria");
                    WinHttpCloseHandle(req); WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
                    free(buf);
                    return 0;
                }
                buf = nb; cap = nc;
            }
            if (!WinHttpReadData(req, buf + n, avail, &got) || !got) break;
            n += (int)got;
        }
        WinHttpCloseHandle(req); WinHttpCloseHandle(con); WinHttpCloseHandle(ses);
        *out = buf; *nlen = n;
        ok = n > 0;
        if (!ok) snprintf(err, 180, "No se ha podido descargar la reducida.");
        return ok;
    }
    snprintf(err, 180, "No se ha podido descargar la reducida.");
    return 0;
}

static int acaba_txt(const char *s) {
    size_t n = strlen(s);
    return n > 4 && tolower((unsigned char)s[n - 4]) == '.' && tolower((unsigned char)s[n - 3]) == 't'
        && tolower((unsigned char)s[n - 2]) == 'x' && tolower((unsigned char)s[n - 1]) == 't';
}

static int primer_txt(const char *dir, char *out, int cap) {
    char pat[MAX_PATH];
    WIN32_FIND_DATAA fd;
    HANDLE h;
    snprintf(pat, sizeof pat, "%s\\*", dir);
    h = FindFirstFileA(pat, &fd);
    if (h == INVALID_HANDLE_VALUE) return 0;
    do {
        char full[MAX_PATH];
        if (fd.cFileName[0] == '.') continue;
        snprintf(full, sizeof full, "%s\\%s", dir, fd.cFileName);
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            if (primer_txt(full, out, cap)) { FindClose(h); return 1; }
        } else if (acaba_txt(fd.cFileName)) {
            snprintf(out, cap, "%s", full);
            FindClose(h);
            return 1;
        }
    } while (FindNextFileA(h, &fd));
    FindClose(h);
    return 0;
}

static void borrar_arbol(const char *dir) {
    char pat[MAX_PATH], full[MAX_PATH];
    WIN32_FIND_DATAA fd;
    HANDLE h;
    snprintf(pat, sizeof pat, "%s\\*", dir);
    h = FindFirstFileA(pat, &fd);
    if (h == INVALID_HANDLE_VALUE) { RemoveDirectoryA(dir); return; }
    do {
        if (!strcmp(fd.cFileName, ".") || !strcmp(fd.cFileName, "..")) continue;
        snprintf(full, sizeof full, "%s\\%s", dir, fd.cFileName);
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) borrar_arbol(full);
        else DeleteFileA(full);
    } while (FindNextFileA(h, &fd));
    FindClose(h);
    RemoveDirectoryA(dir);
}

static int dir_descarga(char *dir, int cap) {
    char tmp[MAX_PATH];
    int i;
    static volatile LONG seq;
    GetTempPathA(MAX_PATH, tmp);
    for (i = 0; i < 100; i++) {
        snprintf(dir, cap, "%sloto14_%lu_%ld", tmp, GetCurrentProcessId(), InterlockedIncrement(&seq));
        if (CreateDirectoryA(dir, NULL)) return 1;
    }
    return 0;
}

static int descargar_reducida(const char *url, int v, int k, uint64_t **out, int *nout, char *err) {
    unsigned char *zipb = NULL;
    int zn = 0, n = 0, cap = 0;
    char dir[MAX_PATH], zip[MAX_PATH], txt[MAX_PATH], cmd[1200];
    FILE *f;
    uint64_t *bets = NULL;
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    DWORD code = 1;
    *out = NULL; *nout = 0;
    anotar("Descargando la reducida récord de Lotoideas...");
    if (!http_bajar(url, &zipb, &zn, err)) return 0;
    if (!dir_descarga(dir, sizeof dir)) {
        free(zipb);
        snprintf(err, 180, "No se ha podido guardar el zip.");
        return 0;
    }
    snprintf(zip, sizeof zip, "%s\\r.zip", dir);
    f = fopen(zip, "wb");
    if (!f) { free(zipb); borrar_arbol(dir); snprintf(err, 180, "No se ha podido guardar el zip."); return 0; }
    fwrite(zipb, 1, (size_t)zn, f);
    fclose(f);
    free(zipb);
    snprintf(cmd, sizeof cmd, "cmd.exe /c tar -xf \"%s\" -C \"%s\"", zip, dir);
    memset(&si, 0, sizeof si);
    si.cb = sizeof si;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        borrar_arbol(dir);
        snprintf(err, 180, "el zip no trae un txt");
        return 0;
    }
    WaitForSingleObject(pi.hProcess, 60000);
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    if (!primer_txt(dir, txt, MAX_PATH)) { borrar_arbol(dir); snprintf(err, 180, "el zip no trae un txt"); return 0; }
    f = fopen(txt, "rb");
    if (!f) { borrar_arbol(dir); snprintf(err, 180, "el zip no trae un txt"); return 0; }
    char linea[512];
    while (fgets(linea, sizeof linea, f)) {
        int nums[MAXN], cn, i, vistos = 0;
        uint64_t b = 0;
        cn = 0;
        {
            char *p = linea;
            while (*p && cn < MAXN) {
                while (*p == ' ' || *p == ',' || *p == '\t' || *p == '\r' || *p == '\n') p++;
                if (!*p) break;
                if (*p < '0' || *p > '9') { p++; continue; }
                nums[cn++] = (int)strtol(p, &p, 10);
            }
        }
        if (!cn) continue;
        for (i = 0; i < cn; i++) {
            if (nums[i] < 1 || nums[i] > v || (b & (1ull << (nums[i] - 1)))) { snprintf(err, 180, "una apuesta del zip no encaja con v y k"); fclose(f); free(bets); borrar_arbol(dir); return 0; }
            b |= 1ull << (nums[i] - 1);
            vistos++;
        }
        if (vistos != k) { snprintf(err, 180, "una apuesta del zip no encaja con v y k"); fclose(f); free(bets); borrar_arbol(dir); return 0; }
        if (n >= cap) {
            int nc = cap ? cap * 2 : 64;
            uint64_t *nb = (uint64_t *)realloc(bets, (size_t)nc * sizeof(uint64_t));
            if (!nb) { fclose(f); free(bets); borrar_arbol(dir); snprintf(err, 180, "sin memoria"); return 0; }
            bets = nb; cap = nc;
        }
        bets[n++] = b;
    }
    fclose(f);
    borrar_arbol(dir);
    if (!n) { free(bets); snprintf(err, 180, "el zip no trae apuestas"); return 0; }
    {
        char msg[80];
        snprintf(msg, sizeof msg, "Reducida leída: %d apuestas.", n);
        anotar(msg);
    }
    *out = bets; *nout = n;
    return 1;
}

static int copiar_bets(uint64_t **out) {
    int n;
    uint64_t *c = NULL;
    EnterCriticalSection(&g_cs);
    n = g_nbets;
    if (n) {
        c = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));
        if (c) memcpy(c, g_bets, (size_t)n * sizeof(uint64_t));
        else n = 0;
    }
    LeaveCriticalSection(&g_cs);
    *out = c;
    return n;
}

static void texto_escrutinio(uint64_t *bets, int n, const char *premio) {
    int nums[MAXN], cn, i, kmax = 0, conteo[MAXN + 1];
    uint64_t prem = 0;
    char buf[2048];
    int pos = 0;
    cn = analizar_numeros(premio, nums, MAXN);
    if (cn < 1) { anotar("Error: Escribe la combinación ganadora."); return; }
    for (i = 0; i < cn; i++) {
        if (nums[i] < 1 || nums[i] > MAXN) { anotar("Error: Escribe la combinación ganadora."); return; }
        prem |= 1ull << (nums[i] - 1);
    }
    memset(conteo, 0, sizeof conteo);
    for (i = 0; i < n; i++) {
        int ac = __builtin_popcountll(bets[i] & prem);
        int kb = __builtin_popcountll(bets[i]);
        if (ac > MAXN) ac = MAXN;
        conteo[ac]++;
        if (kb > kmax) kmax = kb;
    }
    pos += snprintf(buf + pos, sizeof buf - pos, "Escrutinio de %d apuestas.", n);
    for (i = kmax; i >= 0; i--) pos += snprintf(buf + pos, sizeof buf - pos, "\n  %d aciertos: %d", i, conteo[i]);
    anotar(buf);
}

static void meter_top(int *top, int *nf, int num, const int *freq, int mayor) {
    int ult, peor, j, puesto;
    if (*nf == 10) {
        ult = top[9];
        peor = mayor ? (freq[num] < freq[ult] || (freq[num] == freq[ult] && num > ult))
                     : (freq[num] > freq[ult] || (freq[num] == freq[ult] && num > ult));
        if (peor) return;
        puesto = 9;
    } else puesto = (*nf)++;
    top[puesto] = num;
    j = puesto;
    while (j > 0) {
        int a = top[j], b = top[j - 1];
        int sube = mayor ? (freq[a] > freq[b] || (freq[a] == freq[b] && a < b))
                         : (freq[a] < freq[b] || (freq[a] == freq[b] && a < b));
        if (!sube) break;
        top[j - 1] = a;
        top[j] = b;
        j--;
    }
}

static void texto_analisis(uint64_t *bets, int n) {
    int freq[MAXN + 1], i, num, pmin = 99, pmax = 0, nmas = 0, nmenos = 0, pos = 0;
    int mas[10], menos[10];
    long long suma_min = 0, suma_max = 0, suma = 0;
    char buf[2048];
    if (!n) { anotar("No hay apuestas."); return; }
    memset(freq, 0, sizeof freq);
    for (i = 0; i < n; i++) {
        int s = 0, p = 0;
        for (num = 1; num <= MAXN; num++) if (bets[i] & (1ull << (num - 1))) {
            freq[num]++; s += num; if (num % 2 == 0) p++;
        }
        if (i == 0 || s < suma_min) suma_min = s;
        if (i == 0 || s > suma_max) suma_max = s;
        suma += s;
        if (p < pmin) pmin = p;
        if (p > pmax) pmax = p;
    }
    for (num = 1; num <= MAXN; num++) if (freq[num]) {
        meter_top(mas, &nmas, num, freq, 1);
        meter_top(menos, &nmenos, num, freq, 0);
    }
    pos = snprintf(buf, sizeof buf, "Apuestas: %d\nSuma mínima %lld, máxima %lld, media %.2f\nPares por apuesta: mínimo %d, máximo %d\nNúmeros más repetidos: ",
        n, suma_min, suma_max, (double)suma / n, pmin, pmax);
    for (i = 0; i < nmas && pos < (int)sizeof buf - 24; i++)
        pos += snprintf(buf + pos, sizeof buf - pos, "%s%d (%d)", i ? ", " : "", mas[i], freq[mas[i]]);
    pos += snprintf(buf + pos, sizeof buf - pos, "\nNúmeros menos repetidos: ");
    for (i = 0; i < nmenos && pos < (int)sizeof buf - 16; i++)
        pos += snprintf(buf + pos, sizeof buf - pos, "%s%d (%d)", i ? ", " : "", menos[i], freq[menos[i]]);
    anotar(buf);
}

static void texto_estadisticas(uint64_t *bets, int n) {
    int freq[MAXN + 1], dec[8], fin[10], pares = 0, impares = 0, i, num;
    char buf[4096];
    int pos = 0;
    if (!n) { anotar("No hay apuestas."); return; }
    memset(freq, 0, sizeof freq); memset(dec, 0, sizeof dec); memset(fin, 0, sizeof fin);
    for (i = 0; i < n; i++) for (num = 1; num <= MAXN; num++) if (bets[i] & (1ull << (num - 1))) {
        freq[num]++;
        if ((num - 1) / 10 < 8) dec[(num - 1) / 10]++;
        fin[num % 10]++;
        if (num % 2 == 0) pares++; else impares++;
    }
    pos += snprintf(buf + pos, sizeof buf - pos, "Pares %d, impares %d\nPor decena: ", pares, impares);
    {
        int primero = 1;
        for (i = 0; i < 8; i++) if (dec[i] && pos < (int)sizeof buf - 24) {
            pos += snprintf(buf + pos, sizeof buf - pos, "%s%d-%d:%d", primero ? "" : ", ", i * 10 + 1, i * 10 + 10, dec[i]);
            primero = 0;
        }
        primero = 1;
        pos += snprintf(buf + pos, sizeof buf - pos, "\nPor terminación: ");
        for (i = 0; i < 10; i++) if (fin[i] && pos < (int)sizeof buf - 16) {
            pos += snprintf(buf + pos, sizeof buf - pos, "%s%d:%d", primero ? "" : ", ", i, fin[i]);
            primero = 0;
        }
    }
    pos += snprintf(buf + pos, sizeof buf - pos, "\nFrecuencia:");
    for (num = 1; num <= MAXN && pos < (int)sizeof buf - 16; num++) if (freq[num])
        pos += snprintf(buf + pos, sizeof buf - pos, "\n  %02d  %d", num, freq[num]);
    anotar(buf);
}

static void texto_validacion(uint64_t *bets, int n, Job *job) {
    int i, problemas = 0;
    char buf[4096];
    int pos;
    uint64_t *vistos;
    int nv = 0;
    if (!n) { anotar("No hay apuestas que validar."); return; }
    vistos = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));
    pos = snprintf(buf, sizeof buf, "Problemas:");
    for (i = 0; i < n && problemas < 40; i++) {
        int nums[MAXN], nr, j, malo = 0;
        nr = listar(bets[i], MAXN, nums);
        if (nr != job->k) { pos += snprintf(buf + pos, sizeof buf - pos, "\nApuesta %d: no tiene %d números distintos.", i + 1, job->k); problemas++; malo = 1; }
        if (job->nbase) {
            for (j = 0; j < nr; j++) {
                int h = 0, q;
                for (q = 0; q < job->nbase; q++) if (job->base[q] == nums[j]) h = 1;
                if (!h) { pos += snprintf(buf + pos, sizeof buf - pos, "\nApuesta %d: usa un número fuera de la base.", i + 1); problemas++; malo = 1; break; }
            }
        } else {
            int techo = job->v;
            for (j = 0; j < nr; j++) if (nums[j] > techo) techo = nums[j];
            for (j = 0; j < nr; j++) if (nums[j] < 1 || nums[j] > (job->v > techo ? job->v : techo)) {
                pos += snprintf(buf + pos, sizeof buf - pos, "\nApuesta %d: fuera de 1..%d.", i + 1, job->v);
                problemas++; malo = 1; break;
            }
        }
        if (job->filtros.activo && !pasa_filtros(nums, nr, &job->filtros, job->nbase ? 49 : job->v)) {
            pos += snprintf(buf + pos, sizeof buf - pos, "\nApuesta %d: no cumple un filtro.", i + 1);
            problemas++;
        }
        if (!malo) {
            for (j = 0; j < nv; j++) if (vistos[j] == bets[i]) {
                pos += snprintf(buf + pos, sizeof buf - pos, "\nApuesta %d: está repetida.", i + 1);
                problemas++;
                break;
            }
            if (vistos) vistos[nv++] = bets[i];
        }
        if (pos > (int)sizeof buf - 80) break;
    }
    free(vistos);
    if (!problemas) {
        snprintf(buf, sizeof buf, "Válidas: %d apuestas de %d números.", n, job->k);
    }
    anotar(buf);
}

static void texto_garantias(Job *job) {
    const char *url = job->ngrupos ? NULL : buscar_url(job->v, job->k, job->t, job->m);
    char buf[900];
    int pos = snprintf(buf, sizeof buf, "Base de %d números, apuestas de %d.\nGarantía pedida: %d si %d.\nApuestas cargadas: %d.",
        job->v, job->k, job->t, job->m, g_apuestas);
    if (url) pos += snprintf(buf + pos, sizeof buf - pos, "\nHay reducida récord pública de Lotoideas:\n%s", url);
    else pos += snprintf(buf + pos, sizeof buf - pos, "\nNo hay zip de Lotoideas para estos datos.");
    if (g_cob[0]) pos += snprintf(buf + pos, sizeof buf - pos, "\nCobertura %s: %s.", g_nota[0] ? g_nota : "contada", g_cob);
    anotar(buf);
    (void)pos;
}

static DWORD WINAPI hilo(LPVOID p) {
    Job *job = (Job *)p;
    char err[200] = "";
    if (strcmp(job->modo, "usar") == 0) {
        uint64_t *absb = NULL, *reales;
        int n = 0, i;
        char nombre[260], msg[320];
        anotar(job->url);
        if (!descargar_reducida(job->url, job->v, job->k, &absb, &n, err)) {
            char m[240];
            snprintf(m, sizeof m, "Error: %s", err[0] ? err : "descarga");
            anotar(m);
        } else {
            reales = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));
            if (!reales) anotar("Error: sin memoria.");
            else {
                for (i = 0; i < n; i++) reales[i] = mapear(job, absb[i]);
                if (!escribir(reales, n, job->v, job->k, job->t, 0, "lotoideas", nombre)) anotar("Error: no se ha podido guardar.");
                else {
                    publicar_bets(reales, n, job->k, -1);
                    g_v = job->v; g_t = job->t;
                    snprintf(msg, sizeof msg, "Archivo: %s", nombre);
                    anotar(msg);
                    anotar("Guardada la reducida récord de Lotoideas, sin cambiarla.");
                }
            }
            free(absb);
        }
    } else {
        anotar("Preparando los sorteos de la base.");
        Opt *o = opt_nuevo(job);
        if (!o) anotar("Error: sin memoria.");
        else {
            char info[180];
            if (o->exacto)
                snprintf(info, sizeof info, "Sorteos posibles: %llu. La cobertura los cuenta todos.", (unsigned long long)o->total_sorteos);
            else if (o->total_sorteos <= 80000000ull)
                snprintf(info, sizeof info, "Sorteos posibles: %llu. No caben en la búsqueda; el porcentaje los cuenta todos.", (unsigned long long)o->total_sorteos);
            else
                snprintf(info, sizeof info, "Sorteos posibles: %llu. El porcentaje es una estimación.", (unsigned long long)o->total_sorteos);
            anotar(info);
            fijar_nota(o->total_sorteos, o->exacto);
            if (strcmp(job->modo, "mejorar") == 0) {
                uint64_t *absb = NULL;
                int n = 0, i;
                anotar(job->url);
                anotar("Si el recocido no la supera, se guarda la lista de Lotoideas.");
                if (!descargar_reducida(job->url, job->v, job->k, &absb, &n, err)) {
                    char m[240];
                    snprintf(m, sizeof m, "Error: %s", err[0] ? err : "descarga");
                    anotar(m);
                } else {
                    for (i = 0; i < n && !g_parar; i++) agregar(o, absb[i]);
                    free(absb);
                    if (o->nap && !g_parar) optimizar(o, job, -1);
                    guardar_opt(o, job, NULL);
                }
            } else {
                int cantidad = job->cantidad >= 1 ? job->cantidad : 20;
                int semilla = 0;
                if (job->usar_record && !(job->modo_p && job->porc < 99.9995) && job->url[0] && !job->filtros.activo) {
                    uint64_t *absb = NULL;
                    int n = 0, i;
                    char m[240];
                    anotar(job->url);
                    if (!descargar_reducida(job->url, job->v, job->k, &absb, &n, err)) {
                        snprintf(m, sizeof m, "Error: %s", err[0] ? err : "descarga");
                        anotar(m);
                    } else {
                        for (i = 0; i < n && !g_parar; i++) agregar(o, absb[i]);
                        free(absb);
                        semilla = o->nap;
                        snprintf(m, sizeof m, "Parto de la reducida récord de Lotoideas: %d apuestas.", semilla);
                        anotar(m);
                    }
                }
                if (!semilla && !job->modo_p && o->nap < cantidad) generar(o, job, cantidad - o->nap);
                else if (!semilla && job->modo_p) generar(o, job, cantidad);
                if (!semilla && o->nap && !g_parar && cob_de(o) < 99.9995 && !(job->modo_p && cob_de(o) >= job->porc) && job->ciclos)
                    optimizar(o, job, job->modo_p ? job->porc : -1);
                else if (o->nap) {
                    char m[180];
                    double cob = cob_de(o);
                    snprintf(m, sizeof m, "Cobertura %.4f%% con %d apuestas.", cob, o->nap);
                    anotar(m);
                    progreso(m, cob);
                    volcar(o, job, cob);
                }
                guardar_opt(o, job, NULL);
            }
            opt_free(o);
        }
    }
    InterlockedExchange(&g_ocupado, 0);
    free(job);
    return 0;
}

static int lanzar(const char *modo, const char *json, char *err) {
    Job *job;
    const char *url = NULL;
    HANDLE h;
    if (g_ocupado) { snprintf(err, 180, "Ya hay un cálculo en marcha."); return 0; }
    job = (Job *)calloc(1, sizeof *job);
    if (!job) { snprintf(err, 180, "sin memoria"); return 0; }
    if (!parse_datos(json, job, err)) { free(job); return 0; }
    snprintf(job->modo, sizeof job->modo, "%s", modo);
    url = job->ngrupos ? NULL : buscar_url(job->v, job->k, job->t, job->m);
    if ((strcmp(modo, "usar") == 0 || strcmp(modo, "mejorar") == 0) && !url) {
        snprintf(err, 180, "No hay zip público de Lotoideas para esta base y esta garantía, o hay grupos.");
        free(job);
        return 0;
    }
    if (strcmp(modo, "calcular") == 0 && !job->modo_p && job->cantidad < 1) {
        snprintf(err, 180, "El número de apuestas tiene que ser al menos 1.");
        free(job);
        return 0;
    }
    if (url) snprintf(job->url, sizeof job->url, "%s", url);
    InterlockedExchange(&g_parar, 0);
    InterlockedExchange(&g_ocupado, 1);
    h = CreateThread(NULL, 0, hilo, job, 0, NULL);
    if (!h) {
        InterlockedExchange(&g_ocupado, 0);
        free(job);
        snprintf(err, 180, "No se ha podido arrancar el cálculo.");
        return 0;
    }
    CloseHandle(h);
    return 1;
}

static int json_escape(char *dst, int cap, const char *s) {
    int n = 0;
    if (!s) s = "";
    while (*s && n < cap - 2) {
        unsigned char c = (unsigned char)*s++;
        if (c == '"' || c == '\\') {
            if (n + 2 >= cap) break;
            dst[n++] = '\\'; dst[n++] = (char)c;
        } else if (c == '\n') {
            if (n + 2 >= cap) break;
            dst[n++] = '\\'; dst[n++] = 'n';
        } else if (c >= 32) dst[n++] = (char)c;
    }
    dst[n] = 0;
    return n;
}

static void estado_json(char *dst, int cap) {
    char esc[480];
    int i, desde, pos = 0;
    EnterCriticalSection(&g_cs);
    json_escape(esc, sizeof esc, g_ahora);
    pos += snprintf(dst + pos, cap - pos, "{\"ahora\":\"%s\",", esc);
    json_escape(esc, sizeof esc, g_linea);
    pos += snprintf(dst + pos, cap - pos, "\"linea\":\"%s\",\"log\":[", esc);
    desde = g_nlog > 80 ? g_nlog - 80 : 0;
    for (i = desde; i < g_nlog && pos < cap - 80; i++) {
        json_escape(esc, sizeof esc, g_log[i]);
        pos += snprintf(dst + pos, cap - pos, "%s\"%s\"", i == desde ? "" : ",", esc);
    }
    json_escape(esc, sizeof esc, g_cob);
    pos += snprintf(dst + pos, cap - pos, "],\"apuestas\":%d,\"cobertura\":\"%s\",", g_apuestas, esc);
    json_escape(esc, sizeof esc, g_nota);
    pos += snprintf(dst + pos, cap - pos, "\"sobre\":\"%s\",\"exacto\":%s,\"ocupado\":%s,\"lista\":[",
        esc, g_exacto ? "true" : "false", g_ocupado ? "true" : "false");
    for (i = 0; i < g_nbets && pos < cap - 64; i++) {
        int nums[MAXN], nr, j, lp = 0;
        char linea[160];
        nr = listar(g_bets[i], MAXN, nums);
        for (j = 0; j < nr && lp < (int)sizeof linea - 4; j++)
            lp += snprintf(linea + lp, sizeof linea - lp, "%s%02d", j ? " " : "", nums[j]);
        pos += snprintf(dst + pos, cap - pos, "%s\"%s\"", i ? "," : "", linea);
    }
    pos += snprintf(dst + pos, cap - pos, "]}");
    LeaveCriticalSection(&g_cs);
}

static int send_todo(SOCKET s, const char *b, int n) {
    int off = 0;
    while (off < n) {
        int r = send(s, b + off, n - off, 0);
        if (r <= 0) return 0;
        off += r;
    }
    return 1;
}

static void responder(SOCKET s, const char *status, const char *ctype, const char *body, int n) {
    char hdr[256];
    int h = snprintf(hdr, sizeof hdr,
        "HTTP/1.1 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n",
        status, ctype, n);
    send_todo(s, hdr, h);
    if (n > 0) send_todo(s, body, n);
}

static void responder_ok(SOCKET s, int ok, const char *err);

static void responder_error(SOCKET s, const char *err) {
    char buf[240];
    snprintf(buf, sizeof buf, "Error: %s", (err && err[0]) ? err : "no se ha podido hacer.");
    anotar(buf);
    responder_ok(s, 0, err);
}

static void responder_ok(SOCKET s, int ok, const char *err) {
    char buf[600], esc[400];
    if (ok) responder(s, "200 OK", "application/json; charset=utf-8", "{\"ok\":true}", 11);
    else {
        json_escape(esc, sizeof esc, err ? err : "");
        snprintf(buf, sizeof buf, "{\"ok\":false,\"error\":\"%s\"}", esc);
        responder(s, "200 OK", "application/json; charset=utf-8", buf, (int)strlen(buf));
    }
}

static const char SHIM[] =
    "<script>(function(){window.pywebview={api:new Proxy({},{get:function(_,nombre){return function(payload){"
    "return fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:nombre,payload:payload||{}})}).then(function(r){return r.json();});};}})};"
    "window.addEventListener('pagehide',function(){try{navigator.sendBeacon('/cerrar');}catch(e){}});"
    "window.dispatchEvent(new Event('pywebviewready'));})();</script>";

static wchar_t g_dir[MAX_PATH];

#include "v14_html.inc"

static void servir_html(SOCKET s) {
    char *buf, *body;
    static const char falta[] = "Sin memoria para la pantalla.";
    int n = V14_HTML_LEN;
    buf = (char *)malloc((size_t)n + sizeof SHIM + 1);
    if (!buf) { responder(s, "500 Internal Server Error", "text/plain; charset=utf-8", falta, (int)strlen(falta)); return; }
    memcpy(buf, V14_HTML, (size_t)n);
    buf[n] = 0;
    body = strstr(buf, "</body>");
    if (body) {
        memmove(body + (sizeof SHIM - 1), body, strlen(body) + 1);
        memcpy(body, SHIM, sizeof SHIM - 1);
    }
    responder(s, "200 OK", "text/html; charset=utf-8", buf, (int)strlen(buf));
    free(buf);
}

static void api_dispatch(SOCKET s, const char *body) {
    char nombre[32], err[200] = "", premio[512];
    if (!json_str(body, NULL, "nombre", nombre, sizeof nombre)) nombre[0] = 0;
    if (strcmp(nombre, "recurso") == 0) {
        Job job;
        char js[80];
        const char *url = NULL;
        int n = 0;
        if (!parse_datos(body, &job, err)) { responder_error(s, err); return; }
        if (!job.ngrupos && !job.filtros.activo) url = buscar_url(job.v, job.k, job.t, job.m);
        if (url) n = apuestas_de_url(url);
        snprintf(js, sizeof js, "{\"ok\":true,\"recurso\":%d}", n);
        responder(s, "200 OK", "application/json; charset=utf-8", js, (int)strlen(js));
        return;
    }
    if (strcmp(nombre, "estado") == 0) {
        char *js = (char *)malloc(600000);
        if (!js) { responder_ok(s, 0, "sin memoria"); return; }
        estado_json(js, 600000);
        responder(s, "200 OK", "application/json; charset=utf-8", js, (int)strlen(js));
        free(js);
        return;
    }
    if (strcmp(nombre, "limpiar") == 0) {
        limpiar_log();
        responder_ok(s, 1, NULL);
        return;
    }
    raya(nombre);
    if (strcmp(nombre, "parar") == 0) {
        InterlockedExchange(&g_parar, 1);
        anotar("Parar. Se guarda el mejor récord.");
        responder_ok(s, 1, NULL);
        return;
    }
    if (strcmp(nombre, "calcular") == 0 || strcmp(nombre, "usar") == 0 || strcmp(nombre, "mejorar") == 0) {
        if (!lanzar(nombre, body, err)) responder_error(s, err);
        else responder_ok(s, 1, NULL);
        return;
    }
    if (strcmp(nombre, "garantias") == 0) {
        Job job;
        if (!parse_datos(body, &job, err)) { responder_error(s, err); return; }
        texto_garantias(&job);
        responder_ok(s, 1, NULL);
        return;
    }
    if (strcmp(nombre, "escrutar") == 0 || strcmp(nombre, "analizar") == 0 || strcmp(nombre, "estadisticas") == 0
        || strcmp(nombre, "validar") == 0 || strcmp(nombre, "guardar") == 0) {
        uint64_t *b = NULL;
        int n = copiar_bets(&b);
        const char *pay, *fin = NULL;
        if (!n) { free(b); responder_error(s, "Primero calcula, carga o usa una reducida."); return; }
        if (strcmp(nombre, "analizar") == 0) texto_analisis(b, n);
        else if (strcmp(nombre, "estadisticas") == 0) texto_estadisticas(b, n);
        else if (strcmp(nombre, "escrutar") == 0) {
            pay = json_valor(body, NULL, "payload");
            if (pay && *pay == '{') objeto_fin(pay, &fin); else pay = body, fin = NULL;
            json_str(pay, fin, "premio", premio, sizeof premio);
            texto_escrutinio(b, n, premio);
        } else if (strcmp(nombre, "validar") == 0) {
            Job job;
            if (!parse_datos(body, &job, err)) { free(b); responder_error(s, err); return; }
            texto_validacion(b, n, &job);
        } else {
            Job job;
            char nombre_f[260], msg[300];
            int v, k, t;
            if (!parse_datos(body, &job, err)) { v = g_v ? g_v : 8; k = g_k ? g_k : 6; t = g_t ? g_t : 1; }
            else { v = job.v; k = job.k; t = job.t; }
            if (!escribir(b, n, v, k, t, 0, "propio", nombre_f)) { free(b); responder_error(s, "No se ha podido guardar."); return; }
            snprintf(msg, sizeof msg, "Sistema propio guardado: %s", nombre_f);
            anotar(msg);
        }
        free(b);
        responder_ok(s, 1, NULL);
        return;
    }
    if (strcmp(nombre, "cargar") == 0) {
        char file[MAX_PATH] = "";
        OPENFILENAMEA ofn;
        FILE *f;
        uint64_t *bets = NULL;
        int n = 0, cap = 0;
        const char *pay, *fin = NULL;
        if (g_ocupado) { responder_error(s, "Espera a que termine."); return; }
        pay = json_valor(body, NULL, "payload");
        if (pay && *pay == '{') objeto_fin(pay, &fin); else { pay = body; fin = NULL; }
        json_str(pay, fin, "archivo", file, sizeof file);
        if (!file[0]) {
            memset(&ofn, 0, sizeof ofn);
            ofn.lStructSize = sizeof ofn;
            ofn.hwndOwner = GetForegroundWindow();
            ofn.lpstrFilter = "Texto (*.txt)\0*.txt\0Todos (*.*)\0*.*\0";
            ofn.lpstrFile = file;
            ofn.nMaxFile = MAX_PATH;
            ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_EXPLORER;
            if (!GetOpenFileNameA(&ofn)) { responder_ok(s, 1, NULL); return; }
        }
        f = fopen(file, "rb");
        if (!f) { responder_error(s, "No se ha podido leer el archivo."); return; }
        char linea[512];
        int quitadas = 0;
        while (fgets(linea, sizeof linea, f)) {
            int nums[MAXN], cn, i, ya = 0;
            uint64_t b = 0;
            cn = analizar_numeros(linea, nums, MAXN);
            if (!cn) continue;
            for (i = 0; i < cn; i++) if (nums[i] >= 1 && nums[i] <= MAXN) b |= 1ull << (nums[i] - 1);
            for (i = 0; i < n; i++) if (bets[i] == b) { ya = 1; break; }
            if (ya) { quitadas++; continue; }
            if (n >= cap) {
                int nc = cap ? cap * 2 : 64;
                uint64_t *nb = (uint64_t *)realloc(bets, (size_t)nc * sizeof(uint64_t));
                if (!nb) break;
                bets = nb; cap = nc;
            }
            bets[n++] = b;
        }
        fclose(f);
        publicar_bets(bets, n, n ? __builtin_popcountll(bets[0]) : 0, -1);
        {
            char msg[MAX_PATH + 80];
            if (quitadas) snprintf(msg, sizeof msg, "Cargadas %d apuestas desde %s. Quitadas %d repetidas.", n, file, quitadas);
            else snprintf(msg, sizeof msg, "Cargadas %d apuestas desde %s", n, file);
            anotar(msg);
        }
        responder_ok(s, 1, NULL);
        return;
    }
    responder_error(s, "Acción desconocida.");
}

static void atender(SOCKET s);

static DWORD WINAPI atender_hilo(LPVOID p) {
    SOCKET *box = (SOCKET *)p;
    atender(*box);
    free(box);
    return 0;
}

static void atender(SOCKET s) {
    char *req = (char *)malloc(65536);
    int got = 0, total, hl, clen = 0;
    char metodo[8], ruta[256], *q, *hdr, *ini;
    if (!req) { closesocket(s); return; }
    while (got < 65535) {
        int r = recv(s, req + got, 65535 - got, 0);
        if (r <= 0) break;
        got += r;
        req[got] = 0;
        hdr = strstr(req, "\r\n\r\n");
        if (!hdr) continue;
        hl = (int)(hdr - req + 4);
        ini = strstr(req, "Content-Length:");
        if (!ini) ini = strstr(req, "content-length:");
        clen = ini ? atoi(ini + 15) : 0;
        if (clen < 0) clen = 0;
        if (clen > 60000) { responder(s, "413 Payload Too Large", "text/plain", "no", 2); free(req); closesocket(s); return; }
        if (got >= hl + clen) break;
    }
    req[got] = 0;
    metodo[0] = ruta[0] = 0;
    sscanf(req, "%7s %255s", metodo, ruta);
    q = strchr(ruta, '?'); if (q) *q = 0;
    hdr = strstr(req, "\r\n\r\n");
    total = hdr ? (int)(hdr - req + 4) : got;
    if (strcmp(ruta, "/cerrar") == 0) {
        InterlockedExchange(&g_parar, 1);
        InterlockedExchange(&g_salir, 1);
        responder(s, "204 No Content", "text/plain", "", 0);
    } else if (strcmp(metodo, "GET") == 0 && (strcmp(ruta, "/") == 0 || strcmp(ruta, "/v14.html") == 0)) {
        servir_html(s);
    } else if (strcmp(metodo, "POST") == 0 && strcmp(ruta, "/api") == 0) {
        char *body = hdr ? hdr + 4 : req + got;
        if (hdr && total + clen <= got) body[clen] = 0;
        api_dispatch(s, body);
    } else responder(s, "404 Not Found", "text/plain", "no", 2);
    free(req);
    closesocket(s);
}

static int buscar_navegador(char *out) {
    const char *c[] = {
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    };
    int i;
    for (i = 0; i < 4; i++) if (GetFileAttributesA(c[i]) != INVALID_FILE_ATTRIBUTES) { strcpy(out, c[i]); return 1; }
    return 0;
}

static void abrir_ventana(int puerto) {
    char edge[MAX_PATH], url[80], perfil[MAX_PATH], cmd[2048];
    const char *local = getenv("LOCALAPPDATA");
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    snprintf(url, sizeof url, "http://127.0.0.1:%d/", puerto);
    if (local && local[0]) {
        snprintf(perfil, sizeof perfil, "%s\\LottoOptimizerV3_14", local);
        CreateDirectoryA(perfil, NULL);
        snprintf(perfil, sizeof perfil, "%s\\LottoOptimizerV3_14\\edge", local);
    } else snprintf(perfil, sizeof perfil, ".\\edge-perfil");
    CreateDirectoryA(perfil, NULL);
    if (!buscar_navegador(edge)) { ShellExecuteA(NULL, "open", url, NULL, NULL, SW_SHOWNORMAL); return; }
    snprintf(cmd, sizeof cmd, "\"%s\" --app=%s --window-size=1100,860 --user-data-dir=\"%s\" --no-first-run --disable-sync", edge, url, perfil);
    memset(&si, 0, sizeof si);
    si.cb = sizeof si;
    memset(&pi, 0, sizeof pi);
    if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) ShellExecuteA(NULL, "open", url, NULL, NULL, SW_SHOWNORMAL);
    else { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); }
}

static int servir(int puerto_fijo, int abrir) {
    WSADATA w;
    SOCKET srv;
    struct sockaddr_in a;
    int yes = 1;
    if (WSAStartup(MAKEWORD(2, 2), &w)) return 1;
    srv = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (srv == INVALID_SOCKET) return 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, (char *)&yes, sizeof yes);
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    a.sin_port = htons((unsigned short)puerto_fijo);
    if (bind(srv, (struct sockaddr *)&a, sizeof a) || listen(srv, 16)) { closesocket(srv); return 1; }
    {
        int sl = sizeof a;
        getsockname(srv, (struct sockaddr *)&a, &sl);
    }
    if (!abrir) {
        printf("http://127.0.0.1:%d/\n", ntohs(a.sin_port));
        fflush(stdout);
    } else {
        DWORD procs[2];
        if (GetConsoleProcessList(procs, 2) == 1) ShowWindow(GetConsoleWindow(), SW_HIDE);
        abrir_ventana(ntohs(a.sin_port));
    }
    while (!g_salir) {
        SOCKET c = accept(srv, NULL, NULL);
        SOCKET *box;
        HANDLE h;
        if (c == INVALID_SOCKET) break;
        {
            DWORD ms = 8000;
            setsockopt(c, SOL_SOCKET, SO_RCVTIMEO, (char *)&ms, sizeof ms);
        }
        box = (SOCKET *)malloc(sizeof *box);
        if (!box) { closesocket(c); continue; }
        *box = c;
        h = CreateThread(NULL, 0, atender_hilo, box, 0, NULL);
        if (!h) { atender(c); free(box); }
        else CloseHandle(h);
    }
    closesocket(srv);
    {
        int i;
        for (i = 0; i < 500 && g_ocupado; i++) Sleep(10);
    }
    WSACleanup();
    return 0;
}

static int bench(void) {
    Job job;
    Opt *o;
    uint64_t b;
    double cob, t0, t1;
    int i, ok = 1;
    LARGE_INTEGER f, c0, c1;
    filtros_init(&job.filtros);
    memset(&job, 0, sizeof job);
    filtros_init(&job.filtros);
    job.v = 5; job.k = 2; job.t = 2; job.m = 2;
    o = opt_nuevo(&job);
    if (!o || o->universo_n != 10 || !o->exacto) return 1;
    if (!agregar(o, (1ull << 0) | (1ull << 1))) return 1;
    if (agregar(o, (1ull << 0) | (1ull << 1)) != -1) return 1;
    cob = cob_de(o);
    printf("cobertura_par=%.4f n=%d\n", cob, o->universo_n);
    if (cob < 9.9 || cob > 10.1 || o->nap != 1) ok = 0;
    opt_free(o);
    memset(&job, 0, sizeof job);
    filtros_init(&job.filtros);
    job.v = 8; job.k = 6; job.t = 3; job.m = 6; job.universo = 3000;
    o = opt_nuevo(&job);
    if (!o) return 1;
    b = muestra(8, 6);
    if (__builtin_popcountll(b) != 6) ok = 0;
    agregar(o, b);
    cob = cob_de(o);
    printf("cobertura_una=%.4f\n", cob);
    if (cob < 99.9) ok = 0;
    opt_free(o);
    memset(&job, 0, sizeof job);
    filtros_init(&job.filtros);
    job.v = 16; job.k = 6; job.t = 3; job.m = 6; job.universo = 8000;
    o = opt_nuevo(&job);
    if (!o) return 1;
    for (i = 0; i < 30; i++) agregar(o, muestra(16, 6));
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c0);
    for (i = 0; i < 25000; i++) paso(o);
    QueryPerformanceCounter(&c1);
    t0 = (double)c0.QuadPart / (double)f.QuadPart;
    t1 = (double)c1.QuadPart / (double)f.QuadPart;
    printf("pasos=25000 ms=%.1f cob=%.4f\n", (t1 - t0) * 1000.0, o->mejor_cob > 0 ? o->mejor_cob : cob_de(o));
    opt_free(o);
    g_parar = 0;
    g_tope = 2000000;
    memset(&job, 0, sizeof job);
    filtros_init(&job.filtros);
    job.v = 12; job.k = 6; job.t = 4; job.m = 6;
    o = opt_nuevo(&job);
    if (!o || o->universo_n != 924) return 1;
    for (i = 0; i < 6; i++) {
        int guard = 0;
        while (guard < 100 && agregar(o, muestra(12, 6)) < 0) guard++;
    }
    if (o->nap != 6) { opt_free(o); return 1; }
    optimizar(o, &job, 100.0);
    printf("busca12=%.4f ciclos=%llu\n", o->mejor_cob, o->ciclos);
    if (o->mejor_cob < 99.9995) ok = 0;
    opt_free(o);
    g_tope = 0;
    (void)t0;
    return ok ? 0 : 1;
}

static void ir_al_exe(void) {
    wchar_t exe[MAX_PATH], *sl;
    if (!GetModuleFileNameW(NULL, exe, MAX_PATH)) return;
    sl = wcsrchr(exe, L'\\');
    if (!sl) return;
    *sl = 0;
    wcsncpy(g_dir, exe, MAX_PATH - 1);
    g_dir[MAX_PATH - 1] = 0;
    SetCurrentDirectoryW(g_dir);
}

int main(int argc, char **argv) {
    int i, puerto = 0, solo = 0;
    g_rng ^= (uint64_t)GetTickCount64() ^ ((uint64_t)GetCurrentProcessId() << 17);
    if (!g_rng) g_rng = 1;
    InitializeCriticalSection(&g_cs);
    ir_al_exe();
    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--bench") == 0) return bench();
        if (strcmp(argv[i], "--servir") == 0 && i + 1 < argc) { puerto = atoi(argv[++i]); solo = 1; }
    }
    return servir(puerto, !solo);
}
