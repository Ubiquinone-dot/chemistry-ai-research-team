
import os, sys, glob



# API endpoint
def run_mq_experiment():
    """Run a quench-anneal experiment
    
    args:
    **
    returns:
    filepaths dict: dictionary of filepaths to the output files
    {
        'sh_log': 'path/to/log.dat',
        'dump': 'path/to/dump.dat',
        'data': 'path/to/data.dat',
    } 
    """

    os.system(f'qsub submit.sh {density} {anneal_T}')

def format_lammps_mq_sh():
    """Create a bash script to run a quenching simulation
    This quench 
    """


def format_lammps_mq_in(structure, pot, melt, quench, warm, anneal, cool, melt_T, quench_T, anneal_T, cool_T, rand_seed):
    """Create a LAMMPS input file for a quenching simulation
    This quench 
    """

    # MQ params
    melt
    quench
    warm
    anneal
    cool

    # Format the potential, hardcoded for a quip GAP-17 potential for now
    # TODO: make this more general
    pot_path = "carbon.xml"
    PAIR_STYLE = "quip"
    POTENTIAL_LAMMPS = f"""
pair_style {PAIR_STYLE}
pair_coeff * * {pot_path} "" 6"""

    # Format the LAMMPS input file
    infile_str = f"""# LAMMPS-MD file
    
variable melt_steps equal {melt}*1000
variable quench_steps equal {quench}*1000
variable warm_steps equal {warm}*1000
variable anneal_steps equal {anneal}*1000
variable cool_steps equal {cool}*1000

print "Melt  : ${{melt_steps}}fs"
print "Quench: ${{quench_steps}}fs"
print "Warm  : ${{warm_steps}}fs"
print "Anneal: ${{anneal_steps}}fs"
print "Cool  : ${{cool_steps}}fs"

# set logging to append to log.dat
log ./log.dat append

# read in data using appropriate units
units metal # mass = g/mole, distance = Å, time = ps, energy = eV, force = eV/Å
atom_style atomic
read_data ./{structure}.data
mass * 12.011  # all atoms are Carbon and therefore have mass ~12


# settings for potential to use for simulation
{POTENTIAL_LAMMPS}


# settings for simulation
neigh_modify every 1 delay 0 check yes # rebuild neighb. lists after every step
timestep 0.001  # i.e. 1fs timesteps
#pair_coeff * * carbon.xml "Potential xml_label=GAP_2017_1_20_0_21_37_48_267" 6



variable Nfreq equal 100
variable Nevery equal 100
variable Nrepeat equal {Nfreq}/{Nevery}
variable Ndump equal 1000 # every ps
variable nAtoms equal atoms


# what should be updated while simulating?

# ensure that the average momentum is 0 at every timestep
fix removeMomentum all momentum 1 linear 1 1 1 
# compute the temperature
compute T all temp

fix TempAve all ave/time {Nevery} {Nrepeat} {Nfreq} c_T

variable P equal press

fix PressAve all ave/time {Nevery} {Nrepeat} {Nfreq} v_P

variable v equal vol

fix vAve all ave/time {Nevery} {Nrepeat} {Nfreq} v_v

compute PE all pe pair

variable PE_Atom equal c_PE/v_nAtoms

fix PEAve_Atom all ave/time ${Nevery} ${Nrepeat} ${Nfreq} v_PE_Atom

compute MSD all msd

# decide what to print
thermo_style custom step cpu temp f_TempAve press f_PressAve f_PEAve_Atom vol f_vAve c_MSD[4]
# ensure that printing is flushed (i.e. displays while running)
thermo_modify flush yes
thermo ${Nfreq}

dump traj all atom ${Ndump}  ./dumps/${structure}.dump.*.dat

velocity all create ${melt_T} ${rand_seed}

run 0

fix integrate all nvt temp ${melt_T} ${melt_T} 0.1
run ${melt_steps}
unfix integrate

fix integrate all nvt temp ${melt_T} ${quench_T} 0.1
run ${quench_steps} 
unfix integrate

fix integrate all nvt temp ${quench_T} ${anneal_T} 0.1
run ${warm_steps} 
unfix integrate

fix integrate all nvt temp ${anneal_T} ${anneal_T} 0.1
run ${anneal_steps} 
unfix integrate

fix integrate all nvt temp ${anneal_T} ${cool_T} 0.1
run ${cool_steps} 
unfix integrate

write_data ./out.data
"""
    return infile_str

print(lammps_mq_str())