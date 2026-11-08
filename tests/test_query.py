"""
Tests pour les outils de requête Traefik.

Ce module contient les tests unitaires pour les fonctions de formatage
dans query_tools.py.
"""
import pytest
from traefik_mcp.server import list_tools, call_tool, initialize_client

# Import dynamique pour contourner le problème d'import avec modules z_
def get_imported_functions():
    """Importez dynamiquement les fonctions depuis query_tools.py."""
    try:
        from traefik_mcp.tools.query_tools import (
            format_overview as fo,
            format_version as fv,
            format_generic as fg,
            _format_generic_recursive as fgr,
        )
        from traefik_mcp.traefik.models import TraefikOverview
        return fo, fv, fg, fgr, TraefikOverview
    except ImportError:
        # Import alternatif via src (mais peut ne pas fonctionner à cause de z_)
        try:
            from src.traefik_mcp.tools.query_tools import (
                format_overview,
                format_version,
                format_generic,
                _format_generic_recursive as fgr
            )
            from src.traefik_mcp.traefik.models import TraefikOverview
            
            return (
                format_overview,
                format_version,
                format_generic,
                fgr,
                TraefikOverview
            )
        except ImportError:
            raise ImportError(
                "Impossible d'importer query_tools.py ou traefik/models.py. "
                "Vérifier que src/traefik_mcp est dans le PYTHONPATH."
            ) from None


# Charger les fonctions dynamiquement au début du test
_functions = get_imported_functions()
format_overview, format_version, format_generic, _format_generic_recursive, TraefikOverview = _functions


@pytest.fixture
def mock_traefik_overview():
    """Fixture avec des données d'overview typiques."""
    data = {
        "http": {
            "routers": {"total": 3},
            "services": {"total": 8},
            "middlewares": {"total": 5}
        },
        "tcp": {
            "routers": {"total": 2},
            "services": {"total": 4},
            "middlewares": {"total": 3}
        },
        "udp": {
            "routers": {"total": 0},
            "services": {"total": 0},
            "middlewares": {"total": 0}
        },
        "features": {
            "traefik-v1": "true",
            "global": "enabled"
        },
        "providers": [
            "default",
            "local"
        ]
    }
    return TraefikOverview(**data)


@pytest.fixture
def mock_version():
    """Fixture avec des données de version typiques."""
    return {
        "Version": "3.0.0-experimental",
        "Codename": "Gorilla Edition",
        "startDate": "2024-11-04T21:08:28Z"
    }


class TestFormatOverview:
    """Tests pour format_overview."""
    
    def test_format_overview_basic(self, mock_traefik_overview):
        """Test de base avec un overview simple."""
        result = format_overview(mock_traefik_overview)
        
        # Vérification de la structure de base
        assert "## Traefik Overview" in result
        assert "### Components definition" in result
        
        # Vérifier que toutes les valeurs sont présentes
        assert "5" in result  # total_routers
        assert "12" in result  # total_services
        assert "8" in result  # total_middlewares
    
    def test_format_overview_with_features_and_providers(
        self, mock_traefik_overview
    ):
        """Test avec features et providers."""
        result = format_overview(mock_traefik_overview)
        
        # Vérifier que les sections sont présentes (avec ou sans contenu)
        assert "### Features" in result or "### Providers" in result
    
    def test_format_overview_section_titles(self, mock_traefik_overview):
        """Test les titres de section."""
        result = format_overview(mock_traefik_overview)
        
        # Vérifier la présence des différents titres de section
        assert "Summary" in result
        assert "Components definition" in result
        
    def test_format_version_empty_fields(self, mock_version):
        """Test avec des champs vides."""
        version_data = {
            "Version": "",
            "Codename": None,
            "startDate": ""
        }
        result = format_version(version_data)
        
        # La fonction devrait gérer les valeurs vides sans crasher
        assert "## Traefik version" in result
        
    def test_format_version_with_valid_data(self, mock_version):
        """Test avec des données de version valides."""
        result = format_version(mock_version)
        
        # Vérifier que toutes les informations sont présentes
        assert "- **Version** : 3.0.0-experimental" in result
        assert "Gorilla Edition" in result
        assert "2024-11-04T21:08:28Z" in result
        
    def test_format_version_empty_fields(self):
        """Test avec des champs vides."""
        version_data = {
            "Version": "",
            "Codename": None,
            "startDate": ""
        }
        result = format_version(version_data)
        
        assert "## Traefik version" in result


class TestFormatGeneric:
    """Tests pour format_generic."""
    
    def test_format_generic_empty(self):
        """Test avec un objet vide."""
        result = format_generic({})
        # Un dict vide devrait retourner une chaîne vide ou quelque chose de raisonnable
        assert len(result) == 0
    
    def test_format_generic_nested_structure(self):
        """Test avec une structure JSON imbriquée."""
        data = {
            "name": "test-service",
            "ports": [80, 443],
            "labels": {
                "env": "production"
            }
        }
        result = format_generic(data)
        
        assert "- **`test-service`**" in result
    
    def test_format_generic_with_title(self):
        """Test avec un titre."""
        data = {"key": "value"}
        result = format_generic(data, title="Custom Title")
        
        # Vérifier le titre dans le résultat
        assert "Custom Title" in result
        
    def test_format_generic_special_keys(self):
        """Test avec des clés spéciales comme 'name' et 'rule'."""
        data = {
            "name": "my-router",
            "rule": "PathPrefix `/api`",
            "other": "value"
        }
        result = format_generic(data)
        
        # Vérifier la clé spéciale 'name'
        assert "**`my-router`**" in result
        # Vérifier que 'rule' est traité comme une clé spéciale
        assert "Rule:" in result
    
    def test_format_generic_null_and_empty(self):
        """Test avec null et chaînes vides."""
        data = {
            "null_field": None,
            "empty_string": ""
        }
        result = format_generic(data)
        
        # La fonction devrait gérer ces cas sans crasher
        assert "- null_field:" in result
    
    def test_format_generic_with_title_false(self):
        """Test avec use_tables=False."""
        data = {"key": "value"}
        result = format_generic(data, use_tables=False)
        
        assert "key" in result


class TestFormatGenericRecursive:
    """Tests pour _format_generic_recursive."""
    
    def test_format_generic_recursive_empty_list(self):
        """Test avec une liste vide."""
        result = _format_generic_recursive([])
        
        # Une liste vide retourne une chaîne vide
        assert result == ""
        
    def test_format_generic_recursive_nested_dict(self):
        """Test avec un dictionnaire imbriqué."""
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        result = _format_generic_recursive(data)
        
        # Vérifier la structure imbriquée
        assert "- level1:" in result
        
    def test_format_generic_recursive_bool_values(self):
        """Test avec des valeurs booléennes."""
        data = {
            "enabled": True,
            "disabled": False
        }
        result = _format_generic_recursive(data)
        
        # Les booléens doivent être formatés comme `True` ou `true`
        assert ("`True`" in result or "`true`" in result) and \
               ("`False`" in result or "`false`" in result)


class TestIntegration:
    """Tests d'intégration pour le flux complet."""
    
    def test_format_overview_and_version_together(self, mock_traefik_overview, mock_version):
        """Test l'utilisation conjointe de format_overview et format_version."""
        overview_result = format_overview(mock_traefik_overview)
        version_result = format_version(mock_version)
        
        # Les deux résultats devraient être générés correctement
        assert len(overview_result) > 0
        assert len(version_result) > 0
        
    def test_format_generic_with_complex_json_string(self):
        """Test avec une chaîne JSON complexe."""
        json_str = '''{"config": {"timeout": 30, "retries": true}}'''
        result = format_generic(json_str)
        
        # La chaîne devrait être parsée et formatée correctement
        assert "config:" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
