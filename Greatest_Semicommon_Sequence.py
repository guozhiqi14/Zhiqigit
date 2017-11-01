
A = "HOTDESSERT"
B = "ODETOHERTZ"
G = "TOTHESHERY"

def troo(i,j,k):
	if A[i-1] == B[j-1]:
		return True
	if A[i-1] == G[k-1]:
		return True
	if B[j-1] == G[k-1]:
		return True



def Best(i,j,k):
	if i == 0 or j == 0 or k == 0:
		return 0
	else:
		if troo(i,j,k):
			return 1 + Best(i-1,j-1,k-1)
		else:
			return max(Best(i,j,k-1),Best(i,j-1,k),Best(i,j,k-1))


print(Best(len(A),len(B),len(G)))