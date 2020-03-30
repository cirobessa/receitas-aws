import os
import time
import boto
import boto.manage.cmdshell

### Faz o Lancamento de 1 instancia em US-EAST-1 com image do UBUNTU 18.04

def launch_instance(ami='ami-07ebfd5b3428b6f4d',
                    instance_type='t2.micro',
                    key_name='paws',
                    key_extension='.pem',
                    key_dir='~/.ssh',
                    group_name='paws',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='paws',
                    user_data=None,
                    cmd_shell=True,
                    login_user='ubuntu',
                    ssh_passwd=None):


    cmd = None
    #ec2 = boto.connect_ec2()
    ec2 = boto.connect_ec2(debug=2)

    # Verifique se o par de chaves especificado ja' existe.
    # Se recebermos novamente um erro InvalidKeyPair.NotFound do EC2,
    # significa que nao existe e precisamos cria-lo.
    try:
        key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print
            'Creating keypair: %s' % key_name
            # Cria uma chave SSH para usar ao fazer login em instancias.
            key = ec2.create_key_pair(key_name)

            # A AWS armazenara a chave publica, mas a chave privada eh
            # gerada e retornada. Devendo ser armazenada localmente.
            # Salver o Arquivo da chave, com permissao de leitura somente
            # o proprietario do arquivo via chmod 400
            key.save(key_dir)
        else:
            raise

# Verifique se o "Security Group" especificado ja existe.
# Se nao existe sera criado
    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            print
            'Creating Security Group: %s' % group_name
            # Create a security group to control access to instance via SSH.
            group = ec2.create_security_group(group_name,
                                              'A group that allows SSH access')
        else:
            raise


# Adicione uma regra ao "Security Group" para autorizar o trafego SSH
# na porta especificada.
    try:
        group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print
            'Security Group: %s Ja Autorizado' % group_name
        else:
            raise


# Agora inicia a instancia. O metodo run_instances
# tem muitos parametros, mas e tudo o que precisamos
# por enquanto.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data)

# Encontre o objeto Instancia real dentro do objeto Reserva
# retornado por EC2.

    instance = reservation.instances[0]

# A instancia foi lancada, mas ainda nao esta pronta.
# corrida. Vamos aguardar que seu estado mude para 'running'.

    print
    'Esperando pela Instancia'
    while instance.state != 'running':
        print
        '.'
        time.sleep(5)
        instance.update()
    print
    'done'


# Vamos marcar a instancia com a TAG  especificado para que possamos
# identificar mais tarde.
    instance.add_tag(tag)


# A instancia esta em execucao agora, vamos tentar programaticamente
# SSH para a instancia usando o Paramiko via boto CmdShell.

    if cmd_shell:
        key_path = os.path.join(os.path.expanduser(key_dir),
                                key_name + key_extension)
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                           key_path,
                                                           user_name=login_user)

    return (instance, cmd)
