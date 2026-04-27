# Test File [TESTE.ROOT]

## Basic Section [TESTE.BASIC]
This is a basic section content.

## Header Section [TESTE.HEADER]
Content of the header section.
It has multiple lines.

## Parent Section [TESTE.PARENT]
This section contains a child.

### Child Section [TESTE.CHILD]
Child content.

---

## Dependency Section [TESTE.DEP_A]
[DEPENDS: TESTE.DEP_B]
Content A.

## Dependency Section [TESTE.DEP_B]
[DEPENDS: TESTE.DEP_A]
Content B.

## Multi Dependency [TESTE.MULTI]
[DEPENDS: TESTE.BASIC, TESTE.HEADER]
Multi content.

## Unicode Tag [TESTE.AÇÃO]
Content with unicode tag.

## Session Resolution [TESTE.SESSION_PARENT]
This is a parent section.
[TESTE.INNER_1]
Inner content 1.
[TESTE.INNER_2]
Inner content 2.

## Smart Placement Test [TESTE.SMART_1]
Content 1.

## Smart Placement Test [TESTE.SMART_2]
Content 2.