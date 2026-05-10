# Test File [TESTE.ROOT]

## Basic Section [TESTE.BASIC]
This is a basic section content.

## Header Section [TESTE.HEADER]
Header content.

## Parent Section [TESTE.PARENT]
Parent content.

### Child Section [TESTE.CHILD]
Child content.

---

## Unicode Section [TESTE.AÇÃO]
Conteúdo com acentuação.

## Dependency Section [TESTE.DEP_A]
[DEPENDS: TESTE.DEP_B]
Content A.

## Dependency Section [TESTE.DEP_B]
[DEPENDS: TESTE.DEP_A]
Content B.

## Multi Dependency [TESTE.MULTI]
[DEPENDS: TESTE.BASIC, TESTE.HEADER]
Multi content.

## Session Parent [TESTE.SESSION_PARENT]
[TESTE.INNER_1]
[TESTE.INNER_2]
Session content.

## Code Block Test [TESTE.CODE_BLOCK]
```markdown
## This should not be a header [TESTE.INSIDE_CODE]
```
Final line of section.

## Depth A [TESTE.DEPTH_A]
[DEPENDS: TESTE.DEPTH_B]
Level A.

## Depth B [TESTE.DEPTH_B]
[DEPENDS: TESTE.DEPTH_C]
Level B.

## Depth C [TESTE.DEPTH_C]
Level C.

## Smart Placement Test [TESTE.SMART_1]
Content 1.

## Smart Placement Test [TESTE.SMART_2]
Content 2.
